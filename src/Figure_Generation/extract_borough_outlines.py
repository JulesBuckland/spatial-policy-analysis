import pandas as pd
import os

DATA_DIR = os.path.join("01_Data", "Spatial_Data")
INPUT_FILE = os.path.join(DATA_DIR, "map_polygons_final.csv")

def extract_borough_outlines():
    print("Extracting Borough Outlines...")
    df = pd.read_csv(INPUT_FILE)
    
    outlines = []
    
    for borough in df['Borough'].unique():
        borough_df = df[df['Borough'] == borough]
        
        segments = {}
        
        for ring_id in borough_df['ring_id'].unique():
            ring = borough_df[borough_df['ring_id'] == ring_id].sort_values('order')
            coords = list(zip(ring['x'], ring['y']))
            
            for i in range(len(coords) - 1):
                p1 = coords[i]
                p2 = coords[i+1]
                seg = tuple(sorted([p1, p2]))
                segments[seg] = segments.get(seg, 0) + 1
        
        for (p1, p2), count in segments.items():
            if count == 1:
                outlines.append({
                    'Borough': borough,
                    'x': p1[0], 'y': p1[1],
                    'xend': p2[0], 'yend': p2[1]
                })
                
    df_outlines = pd.DataFrame(outlines)
    df_outlines.to_csv(os.path.join(DATA_DIR, "borough_outlines.csv"), index=False)
    print(f"Done. Extracted {len(df_outlines)} boundary segments.")

if __name__ == "__main__":
    extract_borough_outlines()