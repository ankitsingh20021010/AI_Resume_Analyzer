from flask import Flask, render_template, request
from dotenv import load_dotenv
from groq import Groq
import fitz  # PyMuPDF
import os

load_dotenv()

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def analyze_resume(text):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": f"""Analyze this resume and provide:
1. ATS Score (out of 100)
2. Strengths (3-5 points)
3. Weaknesses (3-5 points)
4. Missing Keywords
5. Improvement Suggestions

Resume:
{text}"""
            }
        ]
    )
    return response.choices[0].message.content

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["resume"]
        if file and file.filename.endswith(".pdf"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            text = extract_text_from_pdf(filepath)
            result = analyze_resume(text)
            return render_template("result.html", result=result)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)