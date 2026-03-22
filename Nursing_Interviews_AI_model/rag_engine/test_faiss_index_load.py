from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

index_path = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\clinical_governance_final"

print("🔍 Inițializare HuggingFaceEmbeddings...")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

print("📦 Încărcare FAISS index...")
vectordb = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

print("🔍 Interogare: 'What is clinical governance?'...")
results = vectordb.similarity_search("What is clinical governance?", k=3)

for i, doc in enumerate(results, 1):
    print(f"\n📄 Rezultat {i}:\n{'-'*40}\n{doc.page_content[:800]}")
