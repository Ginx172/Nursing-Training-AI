import sys, os
sys.path.insert(0, r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend')

from utils.rag_engine import RAGEngine

rag = RAGEngine()

nursing_path = r'J:\E-Books\........................._nursing'

# Index the most important folders first
priority_folders = [
    'Nursing Interview',
    'Nursing Interview\\1',
    'A&E',
    'Clinical skills',
    'SafeGuarding',
    'Communication for Nursing',
    'Patient Safety',
    'SBAR',
    'Infection Control_MicroBiology',
    'Mental Health',
    'Critical Care',
    'Palliative',
    'cardio',
    'Nursing Leadership',
    'Care plans',
    'Risk Assessments & Risk Management',
    'Quality Improvement',
    'Nursing',
    'Advanced nursing',
    'Geriatric nursing',
    'Paediatry',
    'Surgical',
    'Pain',
    'Pharma',
    'IV',
    'Anatomy',
    'Physiology',
    'Pathophysiology',
]

total_files = 0
total_chunks = 0

for folder in priority_folders:
    full_path = os.path.join(nursing_path, folder)
    if os.path.exists(full_path):
        print(f'\n{"="*60}')
        print(f'Indexing: {folder}')
        print(f'{"="*60}')
        stats = rag.index_directory(full_path, {"category": folder})
        total_files += stats['files_indexed']
        total_chunks += stats['total_chunks']
        print(f'  -> {stats["files_indexed"]} files, {stats["total_chunks"]} chunks, {stats["errors"]} errors')
    else:
        print(f'SKIP (not found): {folder}')

print(f'\n{"="*60}')
print(f'INDEXING COMPLETE!')
print(f'Total files indexed: {total_files}')
print(f'Total chunks in DB: {rag.get_stats()["total_chunks"]}')
print(f'{"="*60}')
