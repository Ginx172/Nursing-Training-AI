import sys, os
sys.path.insert(0, r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend')

# First verify Ollama is responding
import requests
try:
    r = requests.get('http://localhost:11434/api/tags', timeout=5)
    print(f'Ollama status: OK')
    models = [m['name'] for m in r.json().get('models', [])]
    print(f'Models: {models}')
except Exception as e:
    print(f'Ollama NOT running: {e}')
    print('Start it with: ollama serve')
    exit()

# Quick test with small prompt
print('\nTesting Ollama with simple prompt...')
resp = requests.post('http://localhost:11434/api/generate', json={
    'model': 'llama3.1:8b',
    'prompt': 'Generate 1 nursing interview question about hand hygiene. Reply in 3 lines max.',
    'stream': False,
    'options': {'num_predict': 200, 'temperature': 0.7}
}, timeout=180)
print(f'Response: {resp.json().get("response", "NO RESPONSE")[:300]}')
