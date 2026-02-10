import os
import sqlite3
import pytesseract
import pdfplumber  # We use this because it successfully read your Adobe Scan layer
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from huggingface_hub import InferenceClient
import re

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# PASTE YOUR TOKEN HERE
HF_TOKEN = os.getenv("HF_TOKEN")

REPO_ID = "Qwen/Qwen2.5-72B-Instruct"
client = InferenceClient(token=HF_TOKEN)
# ---------------------------------------------------------

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS notes 
                 (id INTEGER PRIMARY KEY, filename TEXT, original_text TEXT, summary TEXT, quiz TEXT)''')
    conn.commit()
    conn.close()

init_db()

def extract_text(filepath):
    """
    Extracts text. Prioritizes PDF Text Layer because your Adobe Scan 
    has a hidden text layer that the AI can understand, even if it looks messy to humans.
    """
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""
    
    try:
        if ext == 'pdf':
            print("📄 Reading PDF Text Layer...")
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    extract = page.extract_text()
                    if extract:
                        text += extract + "\n"
            
            # If PDF text is basically empty, FALLBACK to OCR
            if len(text.strip()) < 10:
                print("⚠️ No text layer found. Switching to OCR...")
                from pdf2image import convert_from_path
                images = convert_from_path(filepath)
                for img in images:
                    text += pytesseract.image_to_string(img) + "\n"

        elif ext in ['png', 'jpg', 'jpeg']:
            print("🖼️ Reading Image...")
            text = pytesseract.image_to_string(Image.open(filepath))
            
        elif ext == 'txt':
            with open(filepath, 'r') as f:
                text = f.read()
                
    except Exception as e:
        print(f"Extraction Error: {e}")
        return "Error reading file. Please try a different format."

    return text

def generate_ai_content(text):
    if not text.strip():
        return "No text could be found. The file might be blank or unreadable."
    
    # SYSTEM PROMPT: Designed to FIX your messy handwriting errors
    system_instruction = """
    You are an expert study assistant. The user has uploaded HANDWRITTEN notes.
    The raw text will be messy (e.g., "Net (rorewet" instead of "Network").
    
    1. **Decipher**: Use your knowledge of the topic (e.g., Computer Networks, OS) to reconstruct the real meaning.
    2. **Summarize**: Create a clean, HTML-formatted summary of the *corrected* concepts.
    3. **Quiz**: Create 3 multiple-choice questions.
    
    Format:
    <h3>Summary</h3>
    <ul><li>Point 1...</li></ul>
    <h3>Self-Check Quiz</h3>
    <p><strong>Q1: ...</strong><br>A)...<br>B)...<br><strong>Answer: ...</strong></p>
    """

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": f"Here is the messy raw text:\n{text[:6000]}"}
    ]

    print(f"Sending request to {REPO_ID}...") 

    try:
        response = client.chat_completion(
            messages=messages, 
            model=REPO_ID, 
            max_tokens=2000,
            temperature=0.3 
        )
        return response.choices[0].message.content.replace("```html", "").replace("```", "").strip()

    except Exception as e:
        return f"AI Service Error: {e}"

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files: return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '': return jsonify({'error': 'No selected file'})
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    extracted_text = extract_text(filepath)
    ai_result = generate_ai_content(extracted_text)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO notes (filename, original_text, summary, quiz) VALUES (?, ?, ?, ?)", 
              (filename, extracted_text, ai_result, "Included"))
    conn.commit()
    conn.close()

    return jsonify({'filename': filename, 'text': extracted_text, 'result': ai_result})

@app.route('/history')
def get_history():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM notes ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

@app.route('/delete/<int:id>', methods=['DELETE'])
def delete_note(id):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("DELETE FROM notes WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)