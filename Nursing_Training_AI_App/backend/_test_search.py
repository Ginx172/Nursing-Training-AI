import sys
sys.path.insert(0, r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend')
from utils.rag_engine import RAGEngine

rag = RAGEngine()
print(f'Total knowledge chunks: {rag.get_stats()["total_chunks"]:,}')

tests = [
    'How to perform triage assessment in emergency department',
    'Safeguarding vulnerable adults procedures',
    'SBAR handover communication technique',
    'Managing sepsis in acute care',
    'Band 5 nurse interview medication safety question',
    'Pain assessment tools for elderly patients',
    'Infection control hand hygiene protocol',
]

for query in tests:
    print(f'\n{"="*60}')
    print(f'Q: {query}')
    print(f'{"="*60}')
    results = rag.search(query, n_results=2)
    for r in results:
        print(f'  [{r["relevance"]:.4f}] {r["source"][:50]}')
        print(f'  Topic: {r["topic"]}')
        print(f'  {r["text"][:200]}...')
        print()
