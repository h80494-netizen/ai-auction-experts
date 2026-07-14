import os

path = r"c:\Users\llll\Documents\두인경매\바이브코딩\downloads\2025 타경 100709\등기부.pdf"
if os.path.exists(path):
    with open(path, "rb") as f:
        content = f.read()
    print("Length:", len(content))
    print("Content as text:")
    try:
        print(content.decode("utf-8"))
    except Exception as e:
        print("Decode failed:", e)
        print("Raw bytes:", content[:100])
else:
    print("File not found")
