import zipfile
import re
import os

qgz_path = 'C:/Users/llll/Downloads/road.qgz'
output_file = 'scratch/read_qgz_output.txt'

with open(output_file, 'w', encoding='utf-8') as f:
    if not os.path.exists(qgz_path):
        f.write("road.qgz not found\n")
    else:
        z = zipfile.ZipFile(qgz_path)
        f.write(f"Files inside qgz: {z.namelist()}\n")
        qgs_name = z.namelist()[0]
        content = z.read(qgs_name).decode('utf-8', errors='replace')
        
        f.write("\nDatasource paths:\n")
        paths = re.findall(r'datasource="([^"]+)"', content)
        for p in set(paths):
            f.write(f"- {p}\n")
            
        f.write("\nLayer tree layer names:\n")
        layers = re.findall(r'<layer-tree-layer[^>]+name="([^"]+)"', content)
        for l in set(layers):
            f.write(f"- {l}\n")
            
        f.write("\nAll layer sources details:\n")
        # Find maplayer tags to see more detail about the layers
        for ml in re.findall(r'<maplayer[^>]+>(.*?)</maplayer>', content, re.DOTALL):
            name_match = re.search(r'<layername>(.*?)</layername>', ml)
            source_match = re.search(r'<datasource>(.*?)</datasource>', ml)
            provider_match = re.search(r'<provider>(.*?)</provider>', ml)
            if name_match and source_match:
                f.write(f"Layer: {name_match.group(1)}\n")
                f.write(f"  Source: {source_match.group(1)}\n")
                if provider_match:
                    f.write(f"  Provider: {provider_match.group(1)}\n")
                f.write("\n")
