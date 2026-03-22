import os
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import pickle

# 📁 Configurare directoare
SOURCE_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\interview_nhs"
INDEX_SAVE_PATH = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\interview_nhs"

# 🧠 Inițializare embedding model
embedding_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 📦 Citim fișierele .txt
def load_txt_documents(folder_path):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except UnicodeDecodeError:
                with open(file_path, "r", encoding="latin-1") as f:  # fallback
                    text = f.read()
            metadata = {"source": filename}
            docs.append(Document(page_content=text, metadata=metadata))
    return docs

# ✂️ Împărțim textul în bucăți
def split_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    return splitter.split_documents(documents)

# 💾 Salvăm FAISS și metadata
def save_faiss_index(chunks, path):
    if not os.path.exists(path):
        os.makedirs(path)
    db = FAISS.from_documents(chunks, embedding_model)
    db.save_local(path)
    # salvăm și pkl pentru metadata
    with open(os.path.join(path, "index.pkl"), "wb") as f:
        pickle.dump(chunks, f)

# 🚀 Proces principal
def build_index():
    print("📥 Citim fișierele...")
    raw_docs = load_txt_documents(SOURCE_FOLDER)
    print(f"✅ Încărcate {len(raw_docs)} fișiere.")
    
    print("🔍 Împărțim în fragmente...")
    chunks = split_documents(raw_docs)
    print(f"✅ Obținute {len(chunks)} fragmente.")

    print("🧠 Generăm embeddings și salvăm FAISS...")
    save_faiss_index(chunks, INDEX_SAVE_PATH)

    print(f"✅ FAISS salvat în: {INDEX_SAVE_PATH}")

if __name__ == "__main__":
    build_index()
