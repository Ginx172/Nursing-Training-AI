
import os
import shutil
import time
import hashlib
from pathlib import Path
from tqdm import tqdm
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import docx

# === CONFIG ===
main_folder = Path(r"C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/interview_nhs")
secondary_folders = [
    Path(r"C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/Interview NHS"),
    Path(r"C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/Interviuri NHS"),
]
supported_extensions = [".txt", ".pdf", ".docx", ".epub"]
log_path = main_folder / "conversion_errors.log"
use_move_instead_of_copy = True  # 🔁 Setează True pentru MUTARE, False pentru COPIERE

# === FUNCȚII DE CONVERSIE ===
def convert_pdf_to_txt(pdf_path):
    txt_path = pdf_path.with_suffix(".txt")
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text()
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        log_error(pdf_path.name, str(e))
        return None
    return txt_path

def convert_docx_to_txt(docx_path):
    txt_path = docx_path.with_suffix(".txt")
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        log_error(docx_path.name, str(e))
        return None
    return txt_path

def convert_epub_to_txt(epub_path):
    txt_path = epub_path.with_suffix(".txt")
    try:
        book = epub.read_epub(str(epub_path))
        text = ""
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text += soup.get_text(separator="\n", strip=True) + "\n"
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        log_error(epub_path.name, str(e))
        return None
    return txt_path

def convert_to_txt(src_path):
    ext = src_path.suffix.lower()
    if ext == ".txt":
        return src_path
    elif ext == ".pdf":
        return convert_pdf_to_txt(src_path)
    elif ext == ".docx":
        return convert_docx_to_txt(src_path)
    elif ext == ".epub":
        return convert_epub_to_txt(src_path)
    return None

# === UTILITARE ===
def log_error(filename, message):
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"{filename}: {message}\n")

def hash_file(filepath):
    try:
        with open(filepath, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        log_error(filepath.name, f"hashing failed: {e}")
        return None

# === INDEX EXISTENT ===
existing_hashes = {}
for txt_file in main_folder.glob("*.txt"):
    h = hash_file(txt_file)
    if h:
        existing_hashes[h] = txt_file.name

# === TIMER ===
start_time = time.time()
num_processed = 0

# === PROCESARE ===
for folder in secondary_folders:
    if not folder.exists():
        print(f"⚠️ Folderul nu există: {folder}")
        continue
    print(f"\n📂 Verificăm folderul: {folder.name}")
    files = list(folder.glob("*"))
    for file in tqdm(files, desc=f"🔍 {folder.name}"):
        if file.suffix.lower() not in supported_extensions:
            continue
        target_txt_name = file.with_suffix(".txt").name
        try:
            converted_file = convert_to_txt(file)
            if not converted_file or not converted_file.exists():
                continue
            content_hash = hash_file(converted_file)
            if content_hash and content_hash not in existing_hashes:
                dest = main_folder / converted_file.name
                if use_move_instead_of_copy:
                    shutil.move(converted_file, dest)
                else:
                    shutil.copy(converted_file, dest)
                existing_hashes[content_hash] = converted_file.name
                num_processed += 1
                print(f"✅ Procesat: {converted_file.name}")
        except Exception as e:
            log_error(file.name, str(e))

# === TIMP FINAL ===
elapsed = time.time() - start_time
print(f"\n🏁 Proces finalizat în {elapsed:.2f} secunde.")
print(f"📄 Fișiere procesate: {num_processed}")
print(f"📝 Log erori: {log_path if log_path.exists() else 'Fără erori'}")
