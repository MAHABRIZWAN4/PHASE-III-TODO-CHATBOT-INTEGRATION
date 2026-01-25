import os

# Check current directory
print("Current directory:", os.getcwd())

# Check if .env exists
print(".env exists:", os.path.exists('.env'))

# Read file directly
with open('.env', 'r') as f:
    lines = f.readlines()
    for i, line in enumerate(lines):
        if 'DATABASE_URL' in line:
            print(f"Line {i}: {repr(line)}")
            # Try to parse it
            if '=' in line:
                key, value = line.split('=', 1)
                print(f"Key: {repr(key.strip())}")
                print(f"Value: {repr(value.strip())}")
