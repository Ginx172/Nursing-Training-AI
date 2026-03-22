# Fix rag_engine.py - add sys.path fix
import sys, os
rag_path = r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend\utils\rag_engine.py'

with open(rag_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add sys.path at the top after imports
old = 'import chromadb'
new = 'import sys\nsys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))\nimport chromadb'
content = content.replace(old, new, 1)

with open(rag_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed imports in rag_engine.py')
