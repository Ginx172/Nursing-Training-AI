import os
import time
from pathlib import Path
from tqdm import tqdm
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter

# === CONFIG ===
module_name = "Mental Health"
input_folder = f"C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/{module_name}"
output_folder = f"C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/test_faiss_output/{module_name}"

# === INIȚIALIZARE ===
print(f"\n🚀 Încep procesarea modulului: {module_name}")
start = time.time()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")
splitter = CharacterTextSplitter(separator="\n", chunk_size=500, chunk_overlap=50)

txt_files = list(Path(input_folder).rglob("*.txt"))
docs = []

for file in tqdm(txt_files, desc="📄 Procesare fișiere .txt"):
    try:
        loader = TextLoader(str(file), encoding="utf-8")
        documents = loader.load()
        chunks = splitter.split_documents(documents)
        docs.extend(chunks)
    except Exception as e:
        tqdm.write(f"❌ Eroare la {file.name}: {e}")

# === CONSTRUIRE FAISS ===
if docs:
    print(f"\n📦 Construim index FAISS cu {len(docs)} bucăți de text...")
    vectordb = FAISS.from_documents(docs, embeddings)
    os.makedirs(output_folder, exist_ok=True)
    vectordb.save_local(output_folder)
    durata = time.time() - start
    print(f"\n✅ Index FAISS salvat în: {output_folder}")
    print(f"⏱️ Durată totală: {durata:.2f} secunde")
else:
    print("⚠️ Nu s-au procesat documente valide.")
