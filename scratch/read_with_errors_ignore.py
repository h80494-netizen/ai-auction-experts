file_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\backend\ai_analyzer.py"

with open("scratch/encoding_analyzer.txt", "w", encoding="utf-8") as out:
    for enc in ['utf-8', 'cp949']:
        out.write(f"\n--- Encoding {enc} (first 20 lines) ---\n")
        try:
            with open(file_path, "r", encoding=enc, errors="ignore") as f:
                content = f.read()
            lines = content.splitlines()[:25]
            for idx, l in enumerate(lines):
                out.write(f"{idx+1}: {l}\n")
        except Exception as e:
            out.write(f"Error {enc}: {e}\n")

print("Wrote encoding outputs to scratch/encoding_analyzer.txt")
