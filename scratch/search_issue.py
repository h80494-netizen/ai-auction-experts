import os
import glob

def search_files(directory, keyword):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html') or file.endswith('.js'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        for i, line in enumerate(lines):
                            if keyword in line:
                                print(f"{path}:{i+1}: {line.strip()[:100]}")
                except Exception as e:
                    pass

search_files(r'c:\Users\llll\Documents\두인경매\바이브코딩', '이슈')
search_files(r'c:\Users\llll\Documents\두인경매\바이브코딩', '개발행위허가')
