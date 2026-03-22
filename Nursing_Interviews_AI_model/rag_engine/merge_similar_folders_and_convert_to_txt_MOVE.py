
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
grouped_folders = {
    "clinical_governance_merged": [
        "clinical_governance", "Clinical Governance"
    ],
    "mental_health_merged": [
        "mental_health", "Mental Health"
    ],
    "training_clinic_merged": [
        "training_clinic", "Training Clinic"
    ],
}
base_dir = Path(r"C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module")
log_path = base_dir / "merge_conversion_errors.log"
supported_extensions = [".txt", ".pdf", ".docx", ".epub"]

# === FUNCȚII DE CONVERSIE ===
def convert_pdf_to_txt(pdf_path):
    txt_path = pdf_path.with_suffix(".txt")
    try:
        with fitz.open(pdf_path) as doc:
            text = "".join([page.get_text() for page in doc])
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return txt_path
    except Exception as e:
        log_error(pdf_path.name, str(e))
        return None

def convert_docx_to_txt(docx_path):
    txt_path = docx_path.with_suffix(".txt")
    try:
        doc = docx.Document(docx_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return txt_path
    except Exception as e:
        log_error(docx_path.name, str(e))
        return None

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
        return txt_path
    except Exception as e:
        log_error(epub_path.name, str(e))
        return None

def convert_to_txt(path):
    ext = path.suffix.lower()
    if ext == ".txt":
        return path
    elif ext == ".pdf":
        return convert_pdf_to_txt(path)
    elif ext == ".docx":
        return convert_docx_to_txt(path)
    elif ext == ".epub":
        return convert_epub_to_txt(path)
    return None

def log_error(filename, message):
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(f"{filename}: {message}\n")

def hash_file(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception as e:
        log_error(file_path.name, f"hash failed: {e}")
        return None

# === ÎNCEPERE PROCESARE ===
start_time = time.time()
for merged_name, folder_list in grouped_folders.items():
    target_folder = base_dir / merged_name
    target_folder.mkdir(exist_ok=True)

    existing_hashes = {}
    for existing_file in target_folder.glob("*.txt"):
        h = hash_file(existing_file)
        if h:
            existing_hashes[h] = existing_file.name

    print(f"\n📦 Consolidare pentru: {merged_name}")
    all_files = []
    for folder_name in folder_list:
        folder_path = base_dir / folder_name
        if not folder_path.exists():
            print(f"⚠️ Folderul nu există: {folder_path}")
            continue
        all_files.extend(folder_path.glob("*"))

    for file in tqdm(all_files, desc=f"🔍 Procesăm {merged_name}"):
        if file.suffix.lower() not in supported_extensions:
            continue
        converted_file = convert_to_txt(file)
        if not converted_file or not converted_file.exists():
            continue
        content_hash = hash_file(converted_file)
        if content_hash and content_hash not in existing_hashes:
            dest = target_folder / converted_file.name
            shutil.move(converted_file, dest)
            existing_hashes[content_hash] = converted_file.name
            print(f"✅ Mutat: {converted_file.name}")

elapsed = time.time() - start_time
print(f"\n🏁 Finalizat în {elapsed:.2f} secunde.")
print(f"📍 Outputuri: {[name for name in grouped_folders.keys()]}")
print(f"📝 Log: {log_path}")
