import zipfile
import os
import geopandas as gpd
import tempfile
import shutil
import pandas as pd
import warnings

# Suppress the PyOGRIO datetime warning for cleaner output
warnings.filterwarnings("ignore")

zip_path = 'data/전국장기미집행.zip'
temp_dir = tempfile.mkdtemp()
try:
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extract('UPIS_003_20260501_11000.zip', temp_dir)
        seoul_zip_path = os.path.join(temp_dir, 'UPIS_003_20260501_11000.zip')
        
        inner_dir = os.path.join(temp_dir, 'inner')
        os.makedirs(inner_dir, exist_ok=True)
        with zipfile.ZipFile(seoul_zip_path, 'r') as z2:
            z2.extractall(inner_dir)
        
        shp_path = None
        for f in os.listdir(inner_dir):
            if f.endswith('.shp'):
                shp_path = os.path.join(inner_dir, f)
                break
                
        if shp_path:
            try:
                gdf = gpd.read_file(shp_path, encoding='euc-kr')
            except Exception:
                gdf = gpd.read_file(shp_path, encoding='utf-8')
            
            print('EXCUT_SE unique values:', gdf['EXCUT_SE'].unique())
            
            print('\nSample data:')
            for idx, row in gdf.head(5).iterrows():
                print(f"EXCUT_SE: {row.get('EXCUT_SE')}, CREATE_DAT: {row.get('CREATE_DAT')}, NTFC_SN: {row.get('NTFC_SN')}, DGM_NM: {row.get('DGM_NM')}")
finally:
    shutil.rmtree(temp_dir)
