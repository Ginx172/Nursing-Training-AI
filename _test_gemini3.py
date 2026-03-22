import os
from dotenv import load_dotenv

load_dotenv(r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend\.env')
key = os.getenv('GEMINI_API_KEY', '').strip()
print(f'Key starts with: {key[:8]}')
print(f'Key length: {len(key)}')

from google import genai

client = genai.Client(api_key=key)

print('\nTesting Gemini 2.0 Flash...')
response = client.models.generate_content(
    model='gemini-2.0-flash',
    contents='Generate 1 nursing interview question about hand hygiene. Reply in 3 lines max.',
    config={
        'temperature': 0.7,
        'max_output_tokens': 200,
    }
)
print(f'\nResponse:\n{response.text}')
print('\nGemini API OK!')
