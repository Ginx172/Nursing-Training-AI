import sys, os
sys.path.insert(0, r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend')

path = r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend\utils\question_generator.py'

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Increase timeout from 120 to 300
content = content.replace('timeout=120', 'timeout=300')

# Fix 2: Reduce context - use top 4 instead of 8
content = content.replace('all_context[:8]', 'all_context[:4]')

# Fix 3: Limit each chunk to 400 chars
old_ctx = '''f"[From: {c['source']}]\\n{c['text']}" for c in all_context[:4]'''
new_ctx = '''f"[From: {c['source']}]\\n{c['text'][:400]}" for c in all_context[:4]'''
content = content.replace(
    '''f"[From: {c['source']}]\\n{c['text']}" for c in all_context[:4]''',
    new_ctx
)

# Fix 4: Also limit scenario context
content = content.replace(
    '''f"[{r['source']}]\\n{r['text']}" for r in results[:5]''',
    '''f"[{r['source']}]\\n{r['text'][:400]}" for r in results[:3]'''
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed: timeout=300s, reduced context size')
