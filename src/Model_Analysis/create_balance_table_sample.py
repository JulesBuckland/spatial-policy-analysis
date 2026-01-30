import pandas as pd
import glob
import os
import numpy as np

OUTPUT_DIR = os.path.join("03_Output_Logs")
os.makedirs(OUTPUT_DIR, exist_ok=True)
RAW_DIR = os.path.join("01_Data", "Raw_Data")
METADATA_DIR = os.path.join("01_Data", "Metadata")

def create_balance_table():
    print("--- Creating Sample Selection Balance Table ---")
    
    imd = pd.read_csv(os.path.join(RAW_DIR, "deprivation.csv") )
    imd_col = imd.columns[7] # Income Score
    imd = imd[[imd.columns[0], imd_col]]
    imd.columns = ['lsoa21cd', 'Income_Score']
    
    lookup = pd.read_csv(os.path.join(RAW_DIR, "lookup.csv"), dtype=str)
    
    health_files = glob.glob(os.path.join(RAW_DIR, "health_*.csv"))
    included_msoas = set()
    for f in health_files:
        try:
            df = pd.read_csv(f)
            if 'Area Code' in df.columns:
                included_msoas.update(df['Area Code'].unique())
        except: pass
    
    print(f"Included MSOAs: {len(included_msoas)}")
    
    
    elig = pd.read_csv(os.path.join(METADATA_DIR, 'policy_eligibility.csv'))
    
    all_gm_msoas = set(elig['msoa21cd'].unique())
    print(f"Total GM MSOAs (from eligibility): {len(all_gm_msoas)}")
    
    
    lsoa_map = lookup[['lsoa21cd', 'msoa21cd']].drop_duplicates()
    imd_msoa = imd.merge(lsoa_map, on='lsoa21cd').groupby('msoa21cd')['Income_Score'].mean().reset_index()
    
    
    if 'lad21nm' in lookup.columns:
        gm_boroughs = [
            'Bolton', 'Bury', 'Manchester', 'Oldham', 'Rochdale', 
            'Salford', 'Stockport', 'Tameside', 'Trafford', 'Wigan'
        ]
        gm_lsoas = lookup[lookup['lad21nm'].isin(gm_boroughs)]['lsoa21cd'].unique()
        gm_msoa_map = lookup[lookup['lad21nm'].isin(gm_boroughs)][['msoa21cd']].drop_duplicates()
        gm_msoas_set = set(gm_msoa_map['msoa21cd'])
        print(f"identified {len(gm_msoas_set)} GM MSOAs from lookup LAD names")
    else:
        pass

    
    gm_lad_codes = [f'E080000{i:02d}' for i in range(1, 11)] # E08000001 to E08000010
    
    print("Lookup columns:", lookup.columns)
    
    if 'ladcd' in lookup.columns:
        gm_boroughs = [
            'Bolton', 'Bury', 'Manchester', 'Oldham', 'Rochdale', 
            'Salford', 'Stockport', 'Tameside', 'Trafford', 'Wigan'
        ]
        if 'ladnm' in lookup.columns:
             gm_msoas_df = lookup[lookup['ladnm'].isin(gm_boroughs)][['msoa21cd']].drop_duplicates()
        else:
             gm_msoas_df = lookup[lookup['ladcd'].isin(gm_lad_codes)][['msoa21cd']].drop_duplicates()
             
        gm_target_msoas = set(gm_msoas_df['msoa21cd'])
        print(f"Found {len(gm_target_msoas)} GM MSOAs using LAD columns.")
    else:
        print("Cannot identify GM MSOAs (missing LAD codes). Using all available MSOAs as comparison?")
        return

    excluded_msoas = gm_target_msoas - included_msoas
    
    print(f"Included: {len(included_msoas)}")
    print(f"Excluded: {len(excluded_msoas)}")
    
    imd_inc = imd_msoa[imd_msoa['msoa21cd'].isin(included_msoas)]['Income_Score']
    imd_exc = imd_msoa[imd_msoa['msoa21cd'].isin(excluded_msoas)]['Income_Score']
    
    mean_inc = imd_inc.mean()
    mean_exc = imd_exc.mean()
    
    from scipy.stats import ttest_ind
    t_stat, p_val = ttest_ind(imd_inc, imd_exc, nan_policy='omit')
    
    print(f"Included Mean Deprivation: {mean_inc:.3f}")
    print(f"Excluded Mean Deprivation: {mean_exc:.3f}")
    print(f"Difference: {mean_inc - mean_exc:.3f}")
    print(f"P-value: {p_val:.4f}")
    
    with open(os.path.join(OUTPUT_DIR, "sample_balance.txt"), "w") as f:
        f.write("--- Sample Selection Balance (IMD Score) ---\n")
        f.write(f"Included (n={len(imd_inc)}): {mean_inc:.3f}\n")
        f.write(f"Excluded (n={len(imd_exc)}): {mean_exc:.3f}\n")
        f.write(f"Difference: {mean_inc - mean_exc:.3f}\n")
        f.write(f"P-value: {p_val:.4f}\n")

if __name__ == "__main__":
    create_balance_table()
