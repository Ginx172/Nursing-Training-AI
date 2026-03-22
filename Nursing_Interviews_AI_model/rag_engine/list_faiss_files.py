import os

# Calea către folderul FAISS combinat
folder = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\faiss_indexes\clinical_governance_final"

# Verifică dacă folderul există
if not os.path.exists(folder):
    print(f"❌ Folderul nu există: {folder}")
else:
    print(f"📂 Conținutul folderului: {folder}\n")
    files = os.listdir(folder)
    if not files:
        print("⚠️ Folderul este gol.")
    else:
        for fname in files:
            fpath = os.path.join(folder, fname)
            if os.path.isfile(fpath):
                size_mb = os.path.getsize(fpath) / (1024 * 1024)
                print(f"📄 {fname} — {size_mb:.2f} MB")
            else:
                print(f"⚠️ {fname} — nu este fișier normal.")
