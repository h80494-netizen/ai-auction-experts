import zipfile
zip_path = 'data/Gyeonggi_GIS_Shapefiles.zip'
try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        print("Files inside Gyeonggi_GIS_Shapefiles.zip:")
        for name in z.namelist():
            print(f" - {name}")
except Exception as e:
    print("Error listing zip:", e)
