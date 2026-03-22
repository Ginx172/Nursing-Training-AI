from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
import os

# 📂 Cale către fișierele procesate (.txt)
DATA_PATH = "data/processed_text"
INDEX_PATH = "index/"

# 🔹 Încarcă fișierele .txt
def load_text_documents():
    documents = []
    for filename in os.listdir(DATA_PATH):
        if filename.endswith(".txt"):
            file_path = os.path.join(DATA_PATH, filename)
            loader = TextLoader(file_path, encoding="utf-8")
            documents.extend(loader.load())
    return documents

# 🔹 Construiește FAISS și salvează-l
def build_vectorstore(docs):
    print("🔧 Construim indexul FAISS...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = FAISS.from_documents(chunks, embeddings)
    vectordb.save_local(INDEX_PATH)
    return vectordb

# 🔹 RECONSTRUIM mereu indexul (temporar, pentru siguranță)
def load_or_create_vectorstore():
    docs = load_text_documents()
    return build_vectorstore(docs)

# 🔹 Creează lanțul RAG (căutare + LLM local)
def create_rag_chain(vectordb):
    llm = Ollama(model="mistral")
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    return qa_chain

# 🔹 Interfață CLI pentru întrebări
def main():
    vectordb = load_or_create_vectorstore()
    rag_chain = create_rag_chain(vectordb)

    print("\n🤖 AI-ul tău este pregătit! Pune-i o întrebare din documentația ta.")
    print("Scrie `exit` pentru a ieși.\n")

    while True:
        query = input("🟦 Tu: ")
        if query.lower() in ["exit", "quit"]:
            break
        result = rag_chain({"query": query})
        print(f"\n🧠 AI:\n{result['result']}\n")

if __name__ == "__main__":
    main()
