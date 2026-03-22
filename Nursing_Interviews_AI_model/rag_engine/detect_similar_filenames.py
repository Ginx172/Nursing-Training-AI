import os
import time
import difflib
import pandas as pd
from pathlib import Path
from tqdm import tqdm

# === CONFIG ===
base_dir = Path("C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model/rag_engine/sorted_by_module")

# === COLECTARE FIȘIERE ===
all_txt_files = list(base_dir.rglob("*.txt"))
file_info = []

print(f"📁 Scanare fișiere .txt în {base_dir}... Total găsite: {len(all_txt_files)}")

start_time = time.time()

for file in tqdm(all_txt_files, desc="🔍 Colectare info fișiere"):
    try:
        size_mb = round(file.stat().st_size / (1024 * 1024), 2)
        file_info.append({
            "Name": file.name,
            "FullPath": str(file),
            "SizeMB": size_mb,
            "Folder": file.parent.name
        })
    except Exception as e:
        print(f"❌ Eroare la fișierul: {file} -> {e}")

df_files = pd.DataFrame(file_info)

# === DETECTARE NUME ASEMĂNĂTOARE ===
print("\n🔎 Căutare fișiere cu nume asemănătoare...")
similar_groups = []
visited = set()

for i, row_i in tqdm(df_files.iterrows(), total=len(df_files), desc="🔄 Comparare nume fișiere"):
    if i in visited:
        continue
    group = [i]
    name_i = row_i["Name"]
    for j, row_j in df_files.iterrows():
        if j != i and j not in visited:
            similarity = difflib.SequenceMatcher(None, name_i, row_j["Name"]).ratio()
            if similarity > 0.85:
                group.append(j)
    if len(group) > 1:
        similar_groups.append(df_files.loc[group])
        visited.update(group)

# === SALVARE RAPORT
if similar_groups:
    result_df = pd.concat(similar_groups).sort_values(by="Name")
    output_path = base_dir / "similar_named_files_report.csv"
    result_df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\n✅ Gata! Fișiere cu nume similare salvate în:\n{output_path}")
else:
    print("✅ Nu au fost găsite fișiere cu nume foarte asemănătoare.")

end_time = time.time()
print(f"\n⏱️ Timp total de rulare: {round(end_time - start_time, 2)} secunde")
