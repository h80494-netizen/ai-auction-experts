import os

def search_files(directory, keyword):
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if keyword in content:
                        print(f"Found keyword '{keyword}' in {path}")

print("Searching for 'pdf_extractor' or 'extract_text_from_pdf' in codebase:")
search_files("backend", "pdf_extractor")
search_files("backend", "extract_text_from_pdf")
