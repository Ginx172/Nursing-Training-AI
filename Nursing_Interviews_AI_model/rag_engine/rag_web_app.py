import os
import streamlit as st
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain_community.llms import Ollama
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA

DATA_PATH = "data/processed_text"
INDEX_PATH = "index/"

@st.cache_resource(show_spinner=True)
def load_vectorstore_with_feedback():
    faiss_file = os.path.join(INDEX_PATH, "index.faiss")
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L3-v2")

    if os.path.exists(faiss_file):
        st.info("📦 Index FAISS găsit. Îl încarc...")
        return FAISS.load_local(INDEX_PATH, embeddings, allow_dangerous_deserialization=True)
    else:
        st.warning("⚙️ Nu există index FAISS — încep construirea...")
        docs = []
        file_list = [f for f in os.listdir(DATA_PATH) if f.endswith(".txt")]
        progress = st.progress(0, text="🔍 Încărc documentele...")

        for i, filename in enumerate(file_list):
            loader = TextLoader(os.path.join(DATA_PATH, filename), encoding="utf-8")
            docs.extend(loader.load())
            progress.progress((i + 1) / len(file_list), text=f"📄 Procesare: {filename}")

        progress.empty()
        st.info("🧠 Vectorizez și salvez în FAISS...")

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        vectordb = FAISS.from_documents(chunks, embeddings)
        vectordb.save_local(INDEX_PATH)
        st.success("✅ FAISS creat cu succes!")
        return vectordb

@st.cache_resource(show_spinner=False)
def load_chain():
    vectordb = load_vectorstore_with_feedback()
    llm = Ollama(model="mistral")
    return RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=False
    )

# 🔹 UI
st.set_page_config(page_title="Nursing AI Assistant", page_icon="💉")
st.title("🧠 Nursing Interview & Clinical Assistant")
st.write("Pune o întrebare despre conținutul tău 📄")

query = st.text_input("Întrebarea ta:", placeholder="Ex: What leadership topics are covered?")

if query:
    with st.spinner("🔄 AI-ul caută răspunsul..."):
        qa_chain = load_chain()
        result = qa_chain({"query": query})
        st.markdown("### 🧠 Răspuns:")
        st.success(result["result"])
