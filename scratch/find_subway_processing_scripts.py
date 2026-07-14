import os
import glob

print("--- Searching for subway line processing scripts ---")
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".py"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "subway_lines" in content and "CREATE TABLE" in content:
                    print(f"Match: {path}")
            except Exception as e:
                pass
