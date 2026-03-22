import os
import json
import faiss
import pickle
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
import requests
import torch

# 🔧 Config
BASE_FAISS_PATH = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes"
LMSTUDIO_API = "http://localhost:1234/v1/completions"
SESSION_DIR = "sessions"
os.makedirs(SESSION_DIR, exist_ok=True)

# 🧠 Encoder
device = 'cuda' if torch.cuda.is_available() else 'cpu'
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

# 📚 Module list
ANTM_MODULES = {
    "elderly_care": "Private Nursing Homes",
    "emergency_care": "A&E / Emergency",
    "clinical_governance": "Governance & Quality",
    "communication_skills": "Communication & Family Support",
    "obstetrics_gyn": "Maternity / Gynaecology",
    "leadership_training": "Leadership Coaching",
    "mental_health": "Mental Health Support",
    "pediatrics": "Pediatric Clinical Knowledge",
    "clinical_training": "Clinical Scenario Trainer",
    "interview_nhs": "General NHS Interview Sim"
}

# 🔎 FAISS query
def query_faiss(module_key, question, top_k=5):
    folder = os.path.join(BASE_FAISS_PATH, module_key)
    index_path = os.path.join(folder, "index.faiss")
    pkl_path = os.path.join(folder, "index.pkl")

    index = faiss.read_index(index_path)
    with open(pkl_path, "rb") as f:
        texts = pickle.load(f)

    emb = model.encode([question])
    D, I = index.search(np.array(emb).astype("float32"), top_k)
    return [texts[i] for i in I[0]]

# 🧠 Prompt + LM Studio call
def build_prompt(chunks, question):
    context = "\n---\n".join(chunks)
    return f"""
You are a nursing training assistant AI. Use this context to help answer the question below.

Context:
{context}

Question:
{question}
"""

def ask_lmstudio(prompt):
    payload = {
        "model": "mistral",  # sau numele modelului activ în LM Studio
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 512
    }
    response = requests.post(LMSTUDIO_API, json=payload)
    if response.status_code == 200:
        return response.json()["choices"][0]["text"]
    else:
        return f"[ERROR {response.status_code}] {response.text}"

# 💾 Salvează sesiune
def save_session(module, question, context_chunks, ai_response):
    timestamp = datetime.now().strftime("%Y_%m_%d_%H-%M-%S")
    out = {
        "module": module,
        "question": question,
        "context": context_chunks,
        "ai_response": ai_response,
        "timestamp": timestamp
    }
    filename = os.path.join(SESSION_DIR, f"session_{timestamp}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"💾 Sesiune salvată: {filename}")

# ▶️ Main loop
def main():
    print("\n🧠 ANTM - AI Nursing Training Model\nSelectează un modul:")
    keys = list(ANTM_MODULES.keys())
    for i, key in enumerate(keys, 1):
        print(f"[{i}] {ANTM_MODULES[key]}")

    idx = int(input("\nNumăr modul: ").strip()) - 1
    selected_key = keys[idx]
    selected_label = ANTM_MODULES[selected_key]

    question = input(f"\n❓ Întrebarea ta pentru modulul {selected_label}:\n> ")

    print("\n🔎 Căutăm în baza de cunoștințe FAISS...")
    context_chunks = query_faiss(selected_key, question)

    print("\n🤖 Trimitem întrebarea + context către LM Studio...")
    full_prompt = build_prompt(context_chunks, question)
    ai_response = ask_lmstudio(full_prompt)

    print("\n🧠 Răspuns AI:")
    print(ai_response.strip())

    save_session(selected_label, question, context_chunks, ai_response.strip())

if __name__ == "__main__":
    main()
