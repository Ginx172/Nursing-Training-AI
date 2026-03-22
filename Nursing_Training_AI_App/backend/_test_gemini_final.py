# Read key DIRECTLY - no dotenv confusion
key = None
with open(r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend\.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('GEMINI_API_KEY='):
            key = line.split('=', 1)[1].strip()
            break

if not key:
    print('ERROR: GEMINI_API_KEY not found!')
    exit()

print(f'Key: {key[:8]}...{key[-4:]} ({len(key)} chars)')

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
