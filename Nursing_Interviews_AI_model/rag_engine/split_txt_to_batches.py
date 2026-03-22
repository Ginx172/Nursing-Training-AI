import os
import shutil
from pathlib import Path
from tqdm import tqdm
import time
import pandas as pd
from datetime import timedelta
import math

SOURCE_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\sorted_by_module\clinical_governance_merged"
DEST_FOLDER = r"C:\Users\eugdu\MyPythonProjects\Nursing_Interviews_AI_model\rag_engine\batches_clinical_governance"
BATCH_SIZE = 100000

def find_txt_files(folder_path):
    return list(Path(folder_path).rglob("*.txt"))

def split_into_batches(file_paths, batch_size):
    return [file_paths[i:i + batch_size] for i in range(0, len(file_paths), batch_size)]

def copy_files_to_batch(batch, batch_idx, dest_folder):
    batch_folder = os.path.join(dest_folder, f"batch_{batch_idx+1:03d}")
    os.makedirs(batch_folder, exist_ok=True)

    for file_path in tqdm(batch, desc=f"📦 Copiem batch {batch_idx+1}", unit="file"):
        dest_file = os.path.join(batch_folder, os.path.basename(file_path))
        shutil.copy(file_path, dest_file)

def main():
    print(f"📁 Căutăm fișiere .txt în: {SOURCE_FOLDER}")
    start_time = time.time()

    files = find_txt_files(SOURCE_FOLDER)
    total_files = len(files)

    if total_files == 0:
        print("⚠️ Nu s-au găsit fișiere .txt în folderul sursă.")
        return

    print(f"✅ Găsite {total_files} fișiere .txt.")
    batches = split_into_batches(files, BATCH_SIZE)

    batch_log = []
    for idx, batch in enumerate(batches):
        print(f"\n🚀 Procesăm batch {idx+1}/{len(batches)}... (fișiere: {len(batch)})")
        copy_files_to_batch(batch, idx, DEST_FOLDER)
        batch_log.append({"Batch": f"batch_{idx+1:03d}", "Num Files": len(batch)})

    total_time = time.time() - start_time
    print(f"\n✅ Împărțirea finalizată în {timedelta(seconds=int(total_time))}.")
    
    df_log = pd.DataFrame(batch_log)
    print("\n📊 Rezumat:")
    print(df_log)

if __name__ == "__main__":
    main()
