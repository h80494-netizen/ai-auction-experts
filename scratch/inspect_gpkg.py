import os
import fiona

downloads_dir = "C:/Users/llll/Downloads"
output_file = "scratch/inspect_gpkg_output.txt"

with open(output_file, 'w', encoding='utf-8') as f:
    if not os.path.exists(downloads_dir):
        f.write("Downloads folder not found\n")
    else:
        files = os.listdir(downloads_dir)
        gpkg_files = [x for x in files if x.lower().endswith('.gpkg')]
        f.write("GPKG files list:\n")
        for gf in gpkg_files:
            f.write(f"- {gf}\n")
            try:
                path = os.path.join(downloads_dir, gf)
                layers = fiona.listlayers(path)
                f.write(f"  Layers: {layers}\n")
                
                # Check schema of first layer
                with fiona.open(path, layer=layers[0]) as src:
                    f.write(f"  CRS: {src.crs}\n")
                    f.write(f"  Total records: {len(src)}\n")
                    f.write(f"  Schema: {src.schema}\n")
            except Exception as e:
                f.write(f"  Error reading gpkg: {e}\n")
            f.write("\n")
