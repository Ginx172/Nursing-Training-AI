from ebooklib import epub
from bs4 import BeautifulSoup
from pathlib import Path

# === CONFIG ===
epub_path = Path(r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\interview_nhs\Berlitz Cruising and Cruise Ships 2019.epub") # Schimbă cu calea ta
output_txt_path = epub_path.with_suffix(".txt")

# === CONVERSIE ===
def epub_to_text(epub_file):
    book = epub.read_epub(str(epub_file))
    all_text = ""
    for item in book.get_items():
        if item.get_type() == epub.ITEM_DOCUMENT:
            soup = BeautifulSoup(item.get_content(), "html.parser")
            all_text += soup.get_text(separator="\n", strip=True) + "\n"
    return all_text

# === SALVARE ===
try:
    text = epub_to_text(epub_path)
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ Fișier salvat: {output_txt_path}")
except Exception as e:
    print(f"❌ Eroare: {e}")
