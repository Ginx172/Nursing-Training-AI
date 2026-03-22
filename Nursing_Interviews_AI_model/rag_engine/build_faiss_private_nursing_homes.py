
import os
import time
from tqdm import tqdm
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain_huggingface import HuggingFaceEmbeddings

# 🔧 Configurare căi
TXT_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\Private Nursing Homes"
INDEX_OUTPUT_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\private_nursing_homes"

# Verificare fișiere
if not os.path.exists(TXT_FOLDER):
    raise FileNotFoundError(f"Folderul nu există: {TXT_FOLDER}")

txt_files = [f for f in os.listdir(TXT_FOLDER) if f.lower().endswith(".txt")]
if not txt_files:
    raise ValueError("Nu s-au găsit fișiere .txt în folderul specificat.")

# 🔍 Inițializare embeddings
print("🔧 Inițializăm modelul HuggingFaceEmbeddings...")
start_time = time.time()
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 🔄 Pregătire documente
documents = []
print(f"\n📂 Procesăm {len(txt_files)} fișiere .txt...")
for filename in tqdm(txt_files, desc="📄 Încărcare fișiere"):
    file_path = os.path.join(TXT_FOLDER, filename)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            documents.append(Document(page_content=content, metadata={"source": filename}))
    except Exception as e:
        print(f"⚠️ Eroare la fișierul {filename}: {e}")

# 🧠 Construim indexul FAISS
print("\n⚙️ Construim FAISS index...")
vectordb = FAISS.from_documents(documents, embeddings)

# 💾 Salvăm indexul
vectordb.save_local(INDEX_OUTPUT_FOLDER)

# ✅ Gata!
elapsed = time.time() - start_time
print(f"\n✅ Index FAISS creat și salvat în:\n{INDEX_OUTPUT_FOLDER}")
print(f"⏱️ Timp total: {elapsed:.2f} secunde")
