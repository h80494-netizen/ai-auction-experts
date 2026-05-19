import shapefile
import json
import os
import pyproj

shp_path = '서울상권.shp'
# We just need the geometries and TRDAR_CD_N (which we might be able to decode)
sf = shapefile.Reader(shp_path, encoding='utf-8', encodingErrors='replace')

features = []
fields = [f[0] for f in sf.fields[1:]]

# Define projections (EPSG:5181 to EPSG:4326)
from pyproj import Transformer
transformer = Transformer.from_crs("epsg:5181", "epsg:4326", always_xy=True)

def transform_polygon(poly_coords):
    new_poly = []
    for ring in poly_coords:
        new_ring = []
        for x, y in ring:
            lon, lat = transformer.transform(x, y)
            new_ring.append([lon, lat])
        new_poly.append(new_ring)
    return new_poly

def transform_multipolygon(mpoly_coords):
    return [transform_polygon(poly) for poly in mpoly_coords]

count = 0
for sr in sf.shapeRecords():
    geom = sr.shape.__geo_interface__
    
    # Reproject coordinates
    if geom['type'] == 'Polygon':
        geom['coordinates'] = transform_polygon(geom['coordinates'])
    elif geom['type'] == 'MultiPolygon':
        geom['coordinates'] = transform_multipolygon(geom['coordinates'])
        
    props = dict(zip(fields, sr.record))
    
    features.append({
        "type": "Feature",
        "geometry": geom,
        "properties": props
    })
    count += 1

geojson_data = {
    "type": "FeatureCollection",
    "features": features
}

out_path = os.path.join('public', 'data', 'seoul_commercial.geojson')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_data, f)
print(f"Saved {count} commercial areas to {out_path}")
