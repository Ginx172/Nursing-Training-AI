import requests, json

# Test with MINIMAL prompt - no RAG context
prompt = """Generate 2 nursing interview questions about medication safety for Band 5 A&E nurse.

Format as JSON array:
[
  {
    "question": "the question",
    "key_points": ["point1", "point2"],
    "model_answer": "brief answer"
  }
]

Return ONLY JSON."""

print("Sending minimal prompt to Ollama...")
resp = requests.post('http://localhost:11434/api/generate', json={
    'model': 'llama3.1:8b',
    'prompt': prompt,
    'stream': False,
    'options': {'num_predict': 500, 'temperature': 0.7}
}, timeout=300)

result = resp.json().get('response', '')
print(f'\nRaw response ({len(result)} chars):')
print(result[:500])

# Try parse
try:
    start = result.find('[')
    end = result.rfind(']') + 1
    if start >= 0 and end > start:
        questions = json.loads(result[start:end])
        print(f'\nParsed {len(questions)} questions OK!')
        for q in questions:
            print(f"  Q: {q.get('question', 'N/A')[:100]}")
except Exception as e:
    print(f'Parse error: {e}')
