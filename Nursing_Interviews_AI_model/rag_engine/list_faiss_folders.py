import os

# Calea către directorul FAISS
base_path = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes"

# Parcurge conținutul directorului și afișează doar directoarele
folder_names = [name for name in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, name))]

print("🔍 Găsite următoarele foldere FAISS:")
for folder in folder_names:
    print(f"📁 {folder}")
