import os

# 🔍 Folderul de bază (poți schimba dacă e în altă parte)
search_root = "C:/Users/eugdu/MyPythonProjects/Nursing_Interviews_AI_model"

# 🔎 Cuvinte cheie de căutat în numele folderelor
keywords = ["sorted", "module"]

# 📦 Lista în care adăugăm rezultatele
matching_folders = []

# 🔄 Căutăm recursiv prin toate folderele
for root, dirs, files in os.walk(search_root):
    for d in dirs:
        folder_name = d.lower()
        if any(kw in folder_name for kw in keywords):
            full_path = os.path.join(root, d)
            matching_folders.append(full_path)

# 📋 Afișăm rezultatele
if matching_folders:
    print("📁 Foldere găsite:")
    for path in matching_folders:
        print(" -", path)
else:
    print("❌ Nu a fost găsit niciun folder cu 'sorted' sau 'module' în nume.")
