from pathlib import Path

# Calea către folderul cu fișiere .txt
folder_path = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/clinical_governance_merged")

# Căutăm fișiere .txt
txt_files = list(folder_path.glob("*.txt"))

if not txt_files:
    print("❌ Nu s-au găsit fișiere .txt.")
else:
    print(f"✅ Găsite {len(txt_files)} fișiere .txt:")
    for file in txt_files[:10]:  # doar primele 10 pentru test
        print(f" - {file.name} ({file.stat().st_size / 1024:.2f} KB)")
