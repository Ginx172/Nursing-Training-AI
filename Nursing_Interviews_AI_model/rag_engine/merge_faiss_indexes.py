import os
import shutil
from tqdm import tqdm

# Căile sursă
source_folders = [
    r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\Clinical Governance",
    r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\clinical_governance"
]

# Calea destinație
merged_folder = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\clinical_governance_final"
os.makedirs(merged_folder, exist_ok=True)

copied = 0
already_exists = 0

# Colectăm fișierele care trebuie copiate
files_to_copy = []
for folder in source_folders:
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            src = os.path.join(folder, fname)
            dst = os.path.join(merged_folder, fname)
            if os.path.isfile(src) and not os.path.exists(dst):
                files_to_copy.append((src, dst))
            elif os.path.exists(dst):
                already_exists += 1

# Copiem cu progres
print(f"🔄 Copiere fișiere FAISS în {merged_folder}...\n")
for src, dst in tqdm(files_to_copy, desc="📥 Copiere fișiere"):
    try:
        shutil.copy2(src, dst)
        copied += 1
    except Exception as e:
        print(f"❌ Eroare la copiere: {src} → {e}")

# Rezumat
print(f"\n✅ Fișiere copiate: {copied}")
print(f"ℹ️ Fișiere deja existente și păstrate: {already_exists}")
print(f"📁 Total în folderul final: {len(os.listdir(merged_folder))}")
import os
import shutil
from tqdm import tqdm

# Căile sursă
source_folders = [
    r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\Clinical Governance",
    r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\clinical_governance"
]

# Calea destinație
merged_folder = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\clinical_governance_final"
os.makedirs(merged_folder, exist_ok=True)

copied = 0
already_exists = 0

# Colectăm fișierele care trebuie copiate
files_to_copy = []
for folder in source_folders:
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            src = os.path.join(folder, fname)
            dst = os.path.join(merged_folder, fname)
            if os.path.isfile(src) and not os.path.exists(dst):
                files_to_copy.append((src, dst))
            elif os.path.exists(dst):
                already_exists += 1

# Copiem cu progres
print(f"🔄 Copiere fișiere FAISS în {merged_folder}...\n")
for src, dst in tqdm(files_to_copy, desc="📥 Copiere fișiere"):
    try:
        shutil.copy2(src, dst)
        copied += 1
    except Exception as e:
        print(f"❌ Eroare la copiere: {src} → {e}")

# Rezumat
print(f"\n✅ Fișiere copiate: {copied}")
print(f"ℹ️ Fișiere deja existente și păstrate: {already_exists}")
print(f"📁 Total în folderul final: {len(os.listdir(merged_folder))}")
