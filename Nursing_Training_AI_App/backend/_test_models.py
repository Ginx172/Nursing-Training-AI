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

models_to_try = ['gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-1.5-flash']

for model_name in models_to_try:
    print(f'\nTrying {model_name}...')
    try:
        response = client.models.generate_content(
            model=model_name,
            contents='Generate 1 nursing question about hand hygiene. 3 lines max.',
            config={'temperature': 0.7, 'max_output_tokens': 200}
        )
        print(f'SUCCESS!\n{response.text}')
        print(f'\nWORKING MODEL: {model_name}')
        break
    except Exception as e:
        err = str(e)[:150]
        print(f'Failed: {err}')
