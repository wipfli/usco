import json
from rasterio.warp import transform_bounds
import os

def read_bounds(filepath):
    bounds = []
    with open(filepath) as f:
        lines = [line.strip() for line in f.readlines()]
        lines = lines[1:]
        for line in lines:
            parts = line.split(',')
            filename = parts[0]
            left, bottom, right, top, _, __ = [float(a) for a in parts[1:]]
            bounds.append({
                'filename': filename,
                'left': left,
                'bottom': bottom,
                'right': right,
                'top': top,
            })
    return bounds

def to_geojson(data):
    src_crs = "EPSG:3857"
    dst_crs = "EPSG:4326"

    left, bottom, right, top = transform_bounds(
        src_crs, dst_crs,
        data['left'], data['bottom'],
        data['right'], data['top']
    )

    return {
        "type": "Feature",
        "properties": {
            "filename": data["filename"]
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [left, bottom],
                [right, bottom],
                [right, top],
                [left, top],
                [left, bottom]
            ]]
        }
    }

for source in [
    'uscobm',
    'uscofm',
    'uscogm',
    'uscoom',
    'uscopm',
    'uscoqm',
    'uscosm',
    'uscotm',
]:
    out_filepath = f'bounds_{source}.geojson'
    if os.path.isfile(out_filepath):
        continue
    bounds = read_bounds(f'source-store/{source}/bounds.csv')

    features = []
    for item in bounds:
        features.append(to_geojson(item))

    with open(out_filepath, 'w') as f:
        json.dump({'type': 'FeatureCollection', 'features': features}, f, indent=2)
    print(f'wrote {out_filepath}')
