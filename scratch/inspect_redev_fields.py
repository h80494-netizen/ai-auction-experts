# -*- coding: utf-8 -*-
import geopandas as gpd

shp_path = r"c:\Users\llll\Documents\두인경매\바이브코딩\scratch\gris_shp\Gyeonggi_Jeongbi_Guyeok.shp"
gdf = gpd.read_file(shp_path, encoding='cp949')

print("Total rows:", len(gdf))
print("Non-null 'name' count:", gdf['name'].notna().sum())
print("Non-null 'remark' count:", gdf['remark'].notna().sum())

print("\nRows with non-null 'name':")
print(gdf[gdf['name'].notna()][['id', 'name', 'remark']].head(20))

print("\nRows with non-null 'remark':")
print(gdf[gdf['remark'].notna()][['id', 'name', 'remark']].head(20))
