import os
import time
import hashlib
import difflib
from pathlib import Path
from tqdm import tqdm
import pandas as pd

# === CONFIG ===
FOLDER_PATH = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module/Leadership")
SUMMARY_REPORT = FOLDER_PATH / "leadership_classification_summary.csv"
THRESHOLD_SIMILARITY = 0.7  # 70%

# === UTILS ===
def hash_file_content(file_path):
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def is_leadership_related(text):
    keywords = ["leadership", "team management", "delegation", "supervision", "clinical leadership",
                "staff coordination", "mentoring", "communication", "decision making", "mdt", "shift leader"]
    return any(kw in text.lower() for kw in keywords)

def calculate_similarity(text1, text2):
    return difflib.SequenceMatcher(None, text1, text2).ratio()

# === MAIN ===
def scan_leadership_folder(folder: Path):
    start = time.time()
    txt_files = list(folder.glob("*.txt"))
    print(f"[INFO] Găsite {len(txt_files)} fișiere .txt în {folder}")

    seen_hashes = set()
    unique_files = []
    duplicates_removed = []

    # Eliminăm duplicate 100%
    for file_path in tqdm(txt_files, desc="[1/3] Eliminăm duplicate exacte"):
        file_hash = hash_file_content(file_path)
        if file_hash not in seen_hashes:
            seen_hashes.add(file_hash)
            unique_files.append(file_path)
        else:
            duplicates_removed.append(file_path)
            file_path.unlink()

    # Eliminăm duplicate similare (70%+)
    final_files = []
    for i, file1 in enumerate(tqdm(unique_files, desc="[2/3] Eliminăm duplicate similare")):
        with open(file1, "r", encoding="utf-8", errors="ignore") as f1:
            text1 = f1.read()
        is_duplicate = False
        for file2 in final_files:
            with open(file2, "r", encoding="utf-8", errors="ignore") as f2:
                text2 = f2.read()
            if calculate_similarity(text1[:5000], text2[:5000]) >= THRESHOLD_SIMILARITY:
                duplicates_removed.append(file1)
                file1.unlink()
                is_duplicate = True
                break
        if not is_duplicate:
            final_files.append(file1)

    # Clasificăm fișierele
    results = []
    for file_path in tqdm(final_files, desc="[3/3] Clasificăm fișierele după Leadership"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            label = "Leadership" if is_leadership_related(content) else "Possibly Related"
            results.append({"file": file_path.name, "classification": label})
        except Exception as e:
            results.append({"file": file_path.name, "classification": f"Error: {e}"})

    df = pd.DataFrame(results)
    df.to_csv(SUMMARY_REPORT, index=False)
    print(f"✅ Clasificare salvată în: {SUMMARY_REPORT}")
    print(f"🧹 Duplicate eliminate: {len(duplicates_removed)}")
    print(f"⏱️ Timp total: {round(time.time() - start, 2)} secunde")

if __name__ == "__main__":
    scan_leadership_folder(FOLDER_PATH)
