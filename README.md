# Notes_Summarizer

# 🧠 Notes Summarizer (StudyAI)

A **Flask-based AI Notes Summarizer** that allows users to upload notes in **PDF, image, or text format**, extract text using **OCR**, and generate a **clean AI-powered summary with a self-check quiz** using **Hugging Face (Qwen 2.5)**.

This project is designed for **students** to quickly revise study material and test understanding.

---

## ✨ Features

- 📄 Upload **PDF / Image / TXT** notes
- 🔍 Text extraction using:
  - Tesseract OCR (images)
  - pdfplumber (PDFs)
- 🤖 AI-powered **summary + quiz generation**
- 🧾 Stores history in **SQLite database**
- 🎨 Modern responsive UI (HTML, CSS, JS)
- 🔐 Secure token handling using environment variables

---

## 🛠️ Tech Stack

**Backend**
- Python
- Flask
- SQLite
- Hugging Face Inference API

**AI / OCR**
- Qwen 2.5 (72B Instruct)
- pytesseract
- pdfplumber
- Pillow

**Frontend**
- HTML5
- CSS3
- JavaScript
- Font Awesome

---

## 📁 Project Structure

Notes_Summarizer/
│── app.py
│── database.db
│── requirements.txt
│── .gitignore
│── README.md
│
├── templates/
│ ├── index.html
│ └── backup.txt
│
├── static/
│ ├── style.css
│ └── script.js
│
├── uploads/
│
└── venv/ (ignored in Git)

👨‍🎓 Academic Use

This project is suitable for:

Mini Project

AI / ML coursework

Web Development labs

Final year project foundation

📜 License

This project is for educational purposes only.

🙌 Author

Ayush Saini
B.Tech Student
Graphic Era University
