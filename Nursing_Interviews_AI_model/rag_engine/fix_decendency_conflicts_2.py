import subprocess
import sys
import os

def main():
    print("Actualizare dependențe pentru proiectul Nursing_Interviews_AI_model")
    print("==================================================================")
    
    # Sărim peste verificarea mediului virtual, deoarece știm că
    # rulăm deja în mediul virtual nursing_rag
    
    # Instalăm dependențele actualizate
    print("\nActualizez dependențele...")
    dependencies = [
        "langchain>=0.3.24,<1.0.0", 
        "langchain-community>=0.3.23",
        "langchain-core>=0.3.59", 
        "langsmith>=0.1.125,<0.4", 
        "pydantic>=2.5.2,<3.0.0"
    ]
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade"] + dependencies, check=True)
        print("\nDependențele au fost actualizate cu succes!")
        
        # Verificăm instalarea
        print("\nVerific instalarea pachetelor actualizate...")
        for package in dependencies:
            name = package.split(">=")[0].split("<")[0]
            subprocess.run([sys.executable, "-m", "pip", "show", name])
            
    except subprocess.CalledProcessError as e:
        print(f"\nEroare la actualizarea dependențelor: {e}")
        return

if __name__ == "__main__":
    main()