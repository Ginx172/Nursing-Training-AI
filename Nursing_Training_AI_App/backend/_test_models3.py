key = None
with open(r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend\.env', 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line.startswith('GEMINI_API_KEY='):
            key = line.split('=', 1)[1].strip()
            break

print(f'Key: {key[:8]}...{key[-4:]} ({len(key)} chars)')

from google import genai

client = genai.Client(api_key=key)

# First list available models
print('\n=== Available models ===')
try:
    for model in client.models.list():
        if 'gemini' in model.name.lower():
            print(f'  {model.name}')
except Exception as e:
    print(f'Could not list: {str(e)[:100]}')

# Try current models
models_to_try = [
    'gemini-3.1-flash-preview',
    'gemini-3.1-flash-lite-preview',
    'gemini-3.1-pro-preview',
    'gemini-2.5-flash',
    'gemini-2.5-pro',
]

print('\n=== Testing models ===')
for model_name in models_to_try:
    print(f'\nTrying {model_name}...')
    try:
        response = client.models.generate_content(
            model=model_name,
            contents='Generate 1 nursing question about hand hygiene. 3 lines max.',
            config={'temperature': 0.7, 'max_output_tokens': 200}
        )
        print(f'SUCCESS!\n{response.text}')
        print(f'\n*** WORKING MODEL: {model_name} ***')
        break
    except Exception as e:
        err = str(e)[:150]
        print(f'Failed: {err}')
