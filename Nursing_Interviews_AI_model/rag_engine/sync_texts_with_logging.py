import os
import fitz  # PyMuPDF
import docx2txt
from datetime import datetime

BASE_DIR = "data/Career"
OUTPUT_DIR = os.path.join("data", "processed_text")
LOG_FILE = "conversion_log.txt"
EXCLUDE_FOLDERS = {"processed_text", "raw_audio", "raw_convert"}

def ensure_output_folder():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(message)

def filename_key_from_path(path):
    parts = os.path.normpath(path).split(os.sep)
    if len(parts) >= 2:
        folder = parts[-2]
        filename = os.path.splitext(parts[-1])[0]
        return f"{folder}__{filename}.txt"
    else:
        return os.path.basename(path).replace(".pdf", ".txt")

def already_processed(target_name):
    return os.path.exists(os.path.join(OUTPUT_DIR, target_name))

def extract_text_from_pdf(path):
    text = ""
    with fitz.open(path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(path):
    return docx2txt.process(path)

def extract_text_from_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def process_file(full_path, ext, output_name):
    try:
        if ext == ".pdf":
            text = extract_text_from_pdf(full_path)
        elif ext == ".docx":
            text = extract_text_from_docx(full_path)
        elif ext == ".txt":
            text = extract_text_from_txt(full_path)
        else:
            log(f"❌ Format nesuportat: {full_path}")
            return

        output_path = os.path.join(OUTPUT_DIR, output_name)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        log(f"✅ Procesat: {output_name}")
    except Exception as e:
        log(f"⚠️ Eroare la procesarea {full_path}: {e}")

def main():
    ensure_output_folder()
    log("🔄 Pornit procesare fișiere din Career/\n")

    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_FOLDERS]

        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in [".pdf", ".docx", ".txt"]:
                continue

            full_path = os.path.join(root, file)
            output_name = filename_key_from_path(full_path)

            if already_processed(output_name):
                log(f"🔁 Sărit (deja procesat): {output_name}")
                continue

            process_file(full_path, ext, output_name)

    log("\n✅ Finalizat procesarea fișierelor din Career/\n")

if __name__ == "__main__":
    main()
