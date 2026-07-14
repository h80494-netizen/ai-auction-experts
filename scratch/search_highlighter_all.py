import os

def search_files(directory):
    for root, dirs, files in os.walk(directory):
        if 'node_modules' in root or '.git' in root or 'scratch' in root:
            continue
        for file in files:
            if file.endswith(('.html', '.js', '.py')):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        for idx, line in enumerate(f):
                            if 'highlighter-mode' in line or 'btn-highlighter' in line or 'AndOr' in line or 'And/Or' in line or 'OR 기능' in line or 'AND 기능' in line:
                                print(f"Match in {path} at line {idx+1}: {line.strip()}")
                except Exception as e:
                    pass

search_files('.')
