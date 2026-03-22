import os
import time
from pathlib import Path
from tqdm import tqdm
from ebooklib import epub
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader

# === CONFIG ===
module_path = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/Private Nursing Homes")
input_folder = module_path / "raw"
output_folder = module_path / "converted_txt"
os.makedirs(output_folder, exist_ok=True)

# === FUNCȚII DE CONVERSIE ===
def convert_pdf_to_txt(pdf_path):
    try:
        reader = PdfReader(str(pdf_path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as e:
        return f"❌ Error reading PDF: {e}"

def convert_epub_to_txt(epub_path):
    try:
        book = epub.read_epub(str(epub_path))
        text = ""
        for item in book.get_items():
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_content(), "html.parser")
                text += soup.get_text() + "\n"
        return text
    except Exception as e:
        return f"❌ Error reading EPUB: {e}"

# === PROCESARE ===
all_files = list(input_folder.glob("*.pdf")) + list(input_folder.glob("*.epub"))
start_time = time.time()
for i, file in enumerate(tqdm(all_files, desc="📚 Conversie fișiere")):
    print(f"[{i+1}/{len(all_files)}] Procesare: {file.name}")
    if file.suffix.lower() == ".pdf":
        text = convert_pdf_to_txt(file)
    elif file.suffix.lower() == ".epub":
        text = convert_epub_to_txt(file)
    else:
        continue

    if "❌ Error" in text or len(text.strip()) < 10:
        print(f"⚠️ Eroare sau fișier gol: {file.name}")
        continue

    txt_filename = file.stem + ".txt"
    with open(output_folder / txt_filename, "w", encoding="utf-8") as f:
        f.write(text)

duration = time.time() - start_time
print(f"\n✅ Conversie finalizată în {duration:.2f} secunde. Fișiere salvate în: {output_folder}")
