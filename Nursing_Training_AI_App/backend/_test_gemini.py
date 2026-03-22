import os
from dotenv import load_dotenv

# Load .env
load_dotenv(r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend\.env')

key = os.getenv('GEMINI_API_KEY', '')
if not key:
    print('ERROR: GEMINI_API_KEY not found in .env!')
    exit()

print(f'API Key loaded: {key[:10]}...{key[-4:]}')

# Test Gemini
import google.generativeai as genai
genai.configure(api_key=key)

# List available models
print('\nAvailable models:')
for m in genai.list_models():
    if 'generateContent' in [x.name for x in m.supported_generation_methods]:
        print(f'  {m.name}')

# Quick test
print('\nTesting Gemini...')
model = genai.GenerativeModel('gemini-2.0-flash')

response = model.generate_content(
    'Generate 1 nursing interview question about hand hygiene. Reply in 3 lines.',
    generation_config={
        'temperature': 0.7,
        'max_output_tokens': 200,
    }
)
print(f'\nResponse:\n{response.text}')
print('\nGemini API OK!')
