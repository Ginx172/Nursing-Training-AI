import os
import time
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings
from ebooklib import epub
from bs4 import BeautifulSoup
import PyPDF2

# Configurare căi
BASE_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\Private Nursing Homes"
INDEX_OUTPUT_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\private_nursing_homes"
SUPPORTED_EXTENSIONS = [".txt", ".pdf", ".epub"]

def convert_pdf_to_text(file_path):
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = ''
            for page in reader.pages:
                text += page.extract_text() or ''
        return text.strip()
    except Exception as e:
        print(f"⚠️ PDF conversion failed for {file_path}: {e}")
        return ""

def convert_epub_to_text(file_path):
    try:
        book = epub.read_epub(file_path)
        text = ''
        for item in book.items:
            if item.get_type() == epub.EpubHtml:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                text += soup.get_text()
        return text.strip()
    except Exception as e:
        print(f"⚠️ EPUB conversion failed for {file_path}: {e}")
        return ""

def collect_documents(folder):
    documents = []
    for root, _, files in os.walk(folder):
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue
            file_path = os.path.join(root, file)
            try:
                if ext == ".txt":
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                elif ext == ".pdf":
                    content = convert_pdf_to_text(file_path)
                elif ext == ".epub":
                    content = convert_epub_to_text(file_path)
                else:
                    continue
                if content:
                    documents.append(Document(page_content=content, metadata={"source": file}))
            except Exception as e:
                print(f"⚠️ Eroare la {file_path}: {e}")
    return documents

# Inițializare embeddings
print("🔧 Inițializăm HuggingFaceEmbeddings...")
start = time.time()
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Colectare documente
print(f"🔍 Căutăm fișiere .txt, .pdf și .epub în: {BASE_FOLDER}")
documents = collect_documents(BASE_FOLDER)
print(f"📄 {len(documents)} fișiere procesate.")

# Construim indexul
print("⚙️ Construim FAISS index...")
vectordb = FAISS.from_documents(documents, embeddings)
vectordb.save_local(INDEX_OUTPUT_FOLDER)

elapsed = time.time() - start
print(f"✅ Index FAISS salvat în {INDEX_OUTPUT_FOLDER}")
print(f"⏱️ Timp total: {elapsed:.2f} secunde")
