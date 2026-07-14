import os

def search_py_files(query):
    workspace_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩"
    print(f"Scanning Python files in workspace for '{query}'...")
    
    for root, dirs, files in os.walk(workspace_dir):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    for idx, line in enumerate(lines):
                        if query in line:
                            print(f"[MATCH] File: {file_path} | Line {idx+1}: {line.strip()}")
                except Exception:
                    pass

if __name__ == "__main__":
    search_py_files("6060")
