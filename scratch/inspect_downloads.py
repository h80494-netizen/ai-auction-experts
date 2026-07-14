import os
import zipfile

downloads_dir = "C:/Users/llll/Downloads"
output_file = "scratch/inspect_downloads_output.txt"

with open(output_file, 'w', encoding='utf-8') as f:
    if not os.path.exists(downloads_dir):
        f.write("Downloads folder not found\n")
    else:
        files = os.listdir(downloads_dir)
        f.write(f"Total files in Downloads: {len(files)}\n\n")
        
        # Filter zip files
        zip_files = [x for x in files if x.lower().endswith('.zip')]
        f.write("ZIP files list:\n")
        for zf in zip_files:
            f.write(f"- {zf}\n")
            try:
                z = zipfile.ZipFile(os.path.join(downloads_dir, zf))
                f.write(f"  Contents: {z.namelist()[:10]}\n")
            except Exception as e:
                f.write(f"  Error reading zip: {e}\n")
            f.write("\n")
            
        f.write("\nSearch for 'road' or '도로' or 'UQ151' in filenames:\n")
        for x in files:
            if 'road' in x.lower() or '도로' in x or '151' in x or 'uq' in x.lower():
                f.write(f"- {x}\n")
