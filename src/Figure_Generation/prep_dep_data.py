import pandas as pd
import os

RAW_DIR = os.path.join("01_Data", "Raw_Data")
METADATA_DIR = os.path.join("01_Data", "Metadata")
PROCESSED_DIR = os.path.join("01_Data", "Processed_Data")

def prep_deprivation_data():
    imd = pd.read_csv(os.path.join(RAW_DIR, "deprivation.csv") )
    imd_col = imd.columns[7] # Income Score
    imd = imd[[imd.columns[0], imd_col]]
    imd.columns = ['lsoa21cd', 'Income_Score']
    
    lookup = pd.read_csv(os.path.join(RAW_DIR, "lookup.csv"), dtype=str)
    lsoa_map = lookup[['lsoa21cd', 'msoa21cd']].drop_duplicates()
    
    imd_msoa = imd.merge(lsoa_map, on='lsoa21cd').groupby('msoa21cd')['Income_Score'].mean().reset_index()
    
    elig = pd.read_csv(os.path.join(METADATA_DIR, 'policy_eligibility.csv'))
    sample_msoas = set(elig['msoa21cd'].unique())
    
    df_sample = imd_msoa[imd_msoa['msoa21cd'].isin(sample_msoas)].copy()
    
    national_quantiles = imd_msoa['Income_Score'].quantile([0.6, 0.7, 0.8, 0.9])
    
    df_sample.to_csv(os.path.join(PROCESSED_DIR, "deprivation_distribution.csv"), index=False)
    
    with open(os.path.join(PROCESSED_DIR, "quantiles.txt"), "w") as f:
        f.write(f"Top10,{imd_msoa['Income_Score'].quantile(0.9)}\n")
        f.write(f"Top20,{imd_msoa['Income_Score'].quantile(0.8)}\n")
        f.write(f"Top30,{imd_msoa['Income_Score'].quantile(0.7)}\n")
        f.write(f"Top40,{imd_msoa['Income_Score'].quantile(0.6)}\n")

if __name__ == "__main__":
    prep_deprivation_data()
