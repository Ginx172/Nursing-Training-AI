import os
# Read .env manually to debug
with open(r'J:\_Proiect_Nursing_training_AI\Nursing_Training_AI_App\backend\.env', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Lines in .env: {len(lines)}')
for i, line in enumerate(lines):
    line = line.strip()
    if '=' in line:
        key_name = line.split('=')[0]
        key_val = line.split('=', 1)[1]
        # Show only first 8 and last 4 chars of value
        safe = f'{key_val[:8]}...{key_val[-4:]}' if len(key_val) > 12 else '(too short)'
        print(f'  Line {i}: {key_name} = {safe} ({len(key_val)} chars)')
    else:
        print(f'  Line {i}: (empty or no =)')
