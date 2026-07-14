import zipfile
import os

data_dir = r"c:\Users\llll\Documents\두인경매\바이브코딩\data"

zips = [
    "UQ111_용도지역(도시지역)_202602.zip",
    "UQ120_도시계획사업(서울플랜+)_202602 (1).zip"
]

for z_name in zips:
    z_path = os.path.join(data_dir, z_name)
    if os.path.exists(z_path):
        print(f"\n--- Contents of {z_name} ---")
        with zipfile.ZipFile(z_path, 'r') as zip_ref:
            names = zip_ref.namelist()
            print(f"Total files: {len(names)}")
            for name in names[:20]:
                print("  ", name)
            if len(names) > 20:
                print("   ...")
    else:
        print(f"\nFile {z_name} not found in {data_dir}!")
