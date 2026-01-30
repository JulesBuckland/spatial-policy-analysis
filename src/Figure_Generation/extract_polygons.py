import sqlite3
import struct
import pandas as pd
import os

SPATIAL_DIR = os.path.join("01_Data", "Spatial_Data")
RAW_DIR = os.path.join("01_Data", "Raw_Data")
METADATA_DIR = os.path.join("01_Data", "Metadata")
GPKG_PATH = os.path.join(SPATIAL_DIR, "msoa dec 2021 boundaries.gpkg")

def decode_gpkg_geom(blob):
    if blob is None: return []
    magic = blob[0:2]
    if magic != b'GP': return []
    flags = blob[3]
    envelope_contents = (flags >> 1) & 0x07
    envelope_sizes = [0, 32, 48, 48, 64]
    header_size = 8 + envelope_sizes[envelope_contents]
    wkb = blob[header_size:]
    if len(wkb) < 5: return []
    byte_order = wkb[0]
    order_str = '<' if byte_order == 1 else '>'
    geom_type = struct.unpack(order_str + 'I', wkb[1:5])[0]
    rings = []
    if geom_type == 3: # Polygon
        num_rings = struct.unpack(order_str + 'I', wkb[5:9])[0]
        offset = 9
        for _ in range(num_rings):
            num_points = struct.unpack(order_str + 'I', wkb[offset:offset+4])[0]
            offset += 4
            points = []
            for _ in range(num_points):
                x, y = struct.unpack(order_str + 'dd', wkb[offset:offset+16])
                points.append((x, y))
                offset += 16
            rings.append(points)
    elif geom_type == 6: # MultiPolygon
        num_polys = struct.unpack(order_str + 'I', wkb[5:9])[0]
        offset = 9
        for _ in range(num_polys):
            sub_type = struct.unpack(order_str + 'I', wkb[offset+1:offset+5])[0]
            num_rings = struct.unpack(order_str + 'I', wkb[offset+5:offset+9])[0]
            offset += 9
            for _ in range(num_rings):
                num_points = struct.unpack(order_str + 'I', wkb[offset:offset+4])[0]
                offset += 4
                points = []
                for _ in range(num_points):
                    x, y = struct.unpack(order_str + 'dd', wkb[offset:offset+16])
                    points.append((x, y))
                    offset += 16
                rings.append(points)
    return rings

def extract_polygons():
    print("Extracting Polygons from GPKG...")
    conn = sqlite3.connect(GPKG_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT MSOA21CD, SHAPE FROM MSOA_2021_EW_BGC_V3")
    rows = cursor.fetchall()
    conn.close()
    
    lookup = pd.read_csv(os.path.join(RAW_DIR, "lookup.csv"), dtype=str, usecols=['msoa21cd', 'ladnm'])
    gm_boroughs = ['Bolton', 'Bury', 'Manchester', 'Oldham', 'Rochdale', 
                   'Salford', 'Stockport', 'Tameside', 'Trafford', 'Wigan']
    lookup_gm = lookup[lookup['ladnm'].isin(gm_boroughs)].drop_duplicates('msoa21cd')
    gm_msoas = set(lookup_gm['msoa21cd'].unique())
    
    elig = pd.read_csv(os.path.join(METADATA_DIR, 'policy_eligibility.csv'))
    
    poly_data = []
    count = 0
    for msoa_id, blob in rows:
        if msoa_id not in gm_msoas: continue
        
        borough = lookup_gm[lookup_gm['msoa21cd'] == msoa_id]['ladnm'].values[0]
        is_eligible = elig[elig['msoa21cd'] == msoa_id]['Eligible'].values[0] if msoa_id in elig['msoa21cd'].values else 0
        
        rings = decode_gpkg_geom(blob)
        for ring_id, ring in enumerate(rings):
            for i, (x, y) in enumerate(ring):
                poly_data.append({
                    'msoa_id': msoa_id,
                    'ring_id': f"{msoa_id}_{ring_id}",
                    'order': i,
                    'x': x,
                    'y': y,
                    'Eligible': is_eligible,
                    'Borough': borough
                })
        count += 1
        if count % 50 == 0: print(f"Processed {count} MSOAs...")

    df = pd.DataFrame(poly_data)
    df.to_csv(os.path.join(SPATIAL_DIR, "map_polygons_final.csv"), index=False)
    print(f"Done. Extracted {len(df)} points for {count} MSOAs.")

if __name__ == "__main__":
    extract_polygons()