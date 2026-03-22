import os

def rename_files(folder, old_text, new_text):
    for root, _, files in os.walk(folder):
        for file in files:
            if old_text in file:
                old_path = os.path.join(root, file)
                new_name = file.replace(old_text, new_text)
                new_path = os.path.join(root, new_name)

                if os.path.exists(new_path):
                    print(f"\n⚠️ Fișierul există deja: {new_name}")
                    print(f"   📁 {new_path}")
                    choice = input("❓ Vrei să îl suprascrii? (y/n): ").strip().lower()
                    if choice != 'y':
                        print("⏭️ Sărit fișierul.")
                        continue
                    else:
                        try:
                            os.remove(new_path)
                            print("🗑️ Fișierul existent a fost șters.")
                        except Exception as e:
                            print(f"❌ Eroare la ștergere: {e}")
                            continue

                try:
                    os.rename(old_path, new_path)
                    print(f"✅ {file} ➡️ {new_name}")
                except Exception as e:
                    print(f"❌ Eroare la redenumire: {file} - {e}")

if __name__ == "__main__":
    print("🔧 Script redenumire fișiere (cu verificare suprascriere)")
    folder = input("📁 Introdu calea către folderul tău: ").strip('"')
    old = input("🔍 Ce vrei să înlocuiești în numele fișierelor? ").strip()
    new = input("✏️ Cu ce vrei să înlocuiești? (pentru ștergere, lasă gol): ").strip()

    rename_files(folder, old, new)
