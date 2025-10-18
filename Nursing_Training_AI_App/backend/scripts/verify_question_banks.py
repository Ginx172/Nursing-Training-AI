#!/usr/bin/env python3
"""
Script pentru verificarea bateriilor de întrebări generate
"""

import os
import json
from collections import defaultdict
import re

def verify_question_banks():
    """Verifică și afișează statisticile bateriilor de întrebări"""
    
    question_banks_dir = "data/question_banks"
    
    if not os.path.exists(question_banks_dir):
        print("❌ Directorul pentru bateriile de întrebări nu există!")
        return
    
    # Colectează statistici
    total_files = 0
    specialty_count = defaultdict(int)
    band_count = defaultdict(int)
    band_specialty_count = defaultdict(int)
    
    # Verifică fișierele
    for filename in os.listdir(question_banks_dir):
        if filename.endswith('.json'):
            total_files += 1
            
            # Parsează cu regex formatul: {specialty}_{band}_bank_XX.json
            name = filename.replace('.json', '')
            m = re.match(r"^(?P<specialty>.+)_(?P<band>band_[0-9]+)_bank_[0-9]{2}$", name)
            if m:
                specialty = m.group('specialty')
                band = m.group('band')
                band_specialty = f"{specialty}_{band}"
            else:
                # Fișier non-standard: ignoră în statistici (ex: curated manual)
                continue
                
                specialty_count[specialty] += 1
                band_count[band] += 1
                band_specialty_count[band_specialty] += 1
    
    # Afișează statisticile
    print("STATISTICI BATERII INTREBARI GENERATE")
    print("=" * 50)
    print(f"Total fisiere: {total_files}")
    print()
    
    print("DISTRIBUTIE PE SPECIALITATI:")
    for specialty, count in sorted(specialty_count.items()):
        print(f"   {specialty.upper()}: {count} baterii")
    print()
    
    print("DISTRIBUTIE PE BANZI:")
    for band, count in sorted(band_count.items()):
        print(f"   {band.upper()}: {count} baterii")
    print()
    
    print("DISTRIBUTIE DETALIATA (Specialitate + Banda):")
    for band_specialty, count in sorted(band_specialty_count.items()):
        print(f"   {band_specialty.upper()}: {count} baterii")
    print()
    
    # Verifică dacă sunt 30 baterii per specialitate
    expected_per_specialty = 30 * 7  # 30 baterii × 7 banzile
    print("VERIFICARE COMPLETITUDINE:")
    for specialty in specialty_count:
        actual = specialty_count[specialty]
        expected = expected_per_specialty
        status = "OK" if actual == expected else "ERROR"
        print(f"   {specialty.upper()}: {actual}/{expected} {status}")
    
    print()
    print("CONFIGURATIE TARGET:")
    print("   - 9 specialitati")
    print("   - 7 banzile (2-8)")
    print("   - 30 baterii per specialitate")
    print("   - Total asteptat: 1,890 baterii")
    print(f"   - Total generat: {total_files}")
    
    if total_files == 1890:
        print("SUCCES! Toate bateriile au fost generate corect!")
    else:
        print("ATENTIE: Numarul de baterii nu corespunde cu targetul!")

if __name__ == "__main__":
    verify_question_banks()
