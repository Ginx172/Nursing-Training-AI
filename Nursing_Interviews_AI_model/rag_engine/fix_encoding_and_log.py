import os
from pathlib import Path
from tqdm import tqdm
import time

def read_file_with_fallback_encoding(file_path, encodings=["utf-8", "latin1", "windows-1252"]):
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.read(), enc
        except Exception:
            continue
    return None, None

# === CONFIG ===
base_folder = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/Private Nursing Homes/converted_txt")
log_file = base_folder / "encoding_fallback_log.txt"
# ==============

# Verificare folder
if not base_folder.exists():
    print(f"❌ Folderul nu există: {base_folder}")
    exit()

files = list(base_folder.glob("*.txt"))
total_files = len(files)

print(f"🔍 Verific .txt în: {base_folder}")
print(f"📄 Număr fișiere detectate: {total_files}")

start_time = time.time()

with open(log_file, "w", encoding="utf-8") as log:
    for i, file in enumerate(tqdm(files, desc="📊 Procesare fișiere"), 1):
        content, encoding_used = read_file_with_fallback_encoding(file)
        if content is not None:
            log.write(f"[OK] {file.name} — encoding: {encoding_used}\n")
        else:
            log.write(f"[FAILED] {file.name} — encoding not detected\n")

end_time = time.time()
duration = end_time - start_time

print(f"✅ Procesare completă în {duration:.2f} secunde.")
print(f"📝 Log salvat în: {log_file}")
