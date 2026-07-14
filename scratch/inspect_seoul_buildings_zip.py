import zipfile

zip_path = "data/서울건축물수.zip"
try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        print("Files in 서울건축물수.zip:")
        for name in z.namelist():
            print(f" - {name}")
except Exception as e:
    print(f"Error reading zip: {e}")
