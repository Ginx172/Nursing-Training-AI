import os
import pandas as pd
import shutil
from tqdm import tqdm
import time

# Setări
csv_path = "document_summaries.csv"
output_base = "sorted_by_module"

# Mapare nume de module → nume de foldere standardizate
MODULE_NAME_MAP = {
    "Interview NHS": "interview_nhs",
    "Training Clinic": "training_clinic",
    "Leadership": "leadership",
    "Clinical Governance": "clinical_governance",
    "Mental Health": "mental_health",
    "Communication": "communication",
    "Pediatrics": "pediatrics",
    "Gynaecology": "gynaecology"
}

# Încarcă fișierul CSV
df = pd.read_csv(csv_path, encoding="utf-8")
total_files = len(df)

# Start cronometru
start_time = time.time()

# Procesare cu bară de progres
with tqdm(total=total_files, desc="📁 Copiere fișiere", unit="fișier") as pbar:
    for idx, row in df.iterrows():
        source_path = row["Path"]
        modules = row["Suggested Modules"]

        if not isinstance(modules, str) or not os.path.exists(source_path):
            pbar.update(1)
            continue

        module_list = [mod.strip() for mod in modules.split(";") if mod.strip()]

        for module in module_list:
            folder_name = MODULE_NAME_MAP.get(module, module.lower().replace(" ", "_"))
            dest_folder = os.path.join(output_base, folder_name)
            os.makedirs(dest_folder, exist_ok=True)

            dest_path = os.path.join(dest_folder, os.path.basename(source_path))

            # Dacă fișierul există deja, adaugă sufix
            if os.path.exists(dest_path):
                base, ext = os.path.splitext(dest_path)
                dest_path = base + f"_copy_{idx}" + ext

            try:
                shutil.copy2(source_path, dest_path)
            except Exception as e:
                print(f"Eroare la copierea {source_path}: {e}")

        # Afișează live fișierul curent și avansează progresul
        tqdm.write(f"✔️ Procesat: {os.path.basename(source_path)}")
        pbar.update(1)

# Timp total
elapsed = time.time() - start_time
print(f"\n✅ Finalizat în {elapsed:.2f} secunde.")
print(f"📂 Fișiere copiate în: {output_base}")
