import os
import pandas as pd
import docx
from PyPDF2 import PdfReader
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup
import mammoth

data_dir = "data"
results = []

def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def extract_text_from_docx(path):
    doc = docx.Document(path)
    return "\n".join([p.text for p in doc.paragraphs])

def extract_text_from_doc(path):
    with open(path, "rb") as doc_file:
        result = mammoth.extract_raw_text(doc_file)
        return result.value

def extract_text_from_pdf(path):
    reader = PdfReader(path)
    text = ""
    for page in reader.pages[:5]:
        text += page.extract_text() or ""
    return text

def extract_text_from_epub(path):
    book = epub.read_epub(path)
    text = ""
    for item in book.get_items():
        if item.get_type() == ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text += soup.get_text()
    return text


def guess_modules(text):
    text_lower = text.lower()
    modules = []
    if any(x in text_lower for x in ["interview", "band 5", "nhs", "star"]):
        modules.append("Interviuri NHS")
    if any(x in text_lower for x in ["infection", "skin", "clinical training"]):
        modules.append("Training Clinic")
    if any(x in text_lower for x in ["leadership", "management", "delegation"]):
        modules.append("Leadership")
    if "governance" in text_lower or "quality improvement" in text_lower:
        modules.append("Clinical Governance")
    if "mental health" in text_lower or "depression" in text_lower:
        modules.append("Mental Health")
    if "complaint" in text_lower or "communication" in text_lower:
        modules.append("Communication")
    if "pediatric" in text_lower or "neonatal" in text_lower:
        modules.append("Pediatrics")
    if "gynae" in text_lower or "obstetric" in text_lower:
        modules.append("Gynaecology")
    return modules

# Parcurge folderul data/
for root, dirs, files in os.walk(data_dir):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        path = os.path.join(root, file)
        text = ""
        try:
            if ext == ".txt":
                text = extract_text_from_txt(path)
            elif ext == ".docx":
                text = extract_text_from_docx(path)
            elif ext == ".doc":
                text = extract_text_from_doc(path)
            elif ext == ".pdf":
                text = extract_text_from_pdf(path)
            elif ext == ".epub":
                text = extract_text_from_epub(path)
        except Exception as e:
            print(f"Eroare la {file}: {e}")
            continue

        if text:
            results.append({
                "Document": file,
                "Path": path,
                "Extract": text[:800].replace("\n", " "),
                "Suggested Modules": "; ".join(guess_modules(text))
            })

# Salvează rezultatele în CSV
df = pd.DataFrame(results)
output_path = "document_summaries.csv"
df.to_csv(output_path, index=False, encoding="utf-8")
print(f"✅ Rezumat salvat în: {output_path}")
