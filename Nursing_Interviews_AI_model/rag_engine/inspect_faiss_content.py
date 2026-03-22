import pickle
import os

folder = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\elderly_care"
pkl_path = os.path.join(folder, "index.pkl")

with open(pkl_path, "rb") as f:
    texts = pickle.load(f)

print(f"🔍 Total fragmente în acest FAISS: {len(texts)}")
print("\n📄 Primele 5 exemple:\n")

for i, t in enumerate(texts[:5], 1):
    print(f"[{i}] {t}\n")
