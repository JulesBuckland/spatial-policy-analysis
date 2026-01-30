import pandas as pd
import glob
import os
import numpy as np

DATA_DIR = os.path.join("model", "data")
OUTPUT_DIR = os.path.join("model", "output", "v4_did")

def investigate():
    print("--- Investigating Anomalies ---")
    
    elig = pd.read_csv(os.path.join(DATA_DIR, 'policy_eligibility.csv'))
    imd = pd.read_csv(os.path.join(DATA_DIR, "deprivation.csv"))
    imd_col = imd.columns[7]
    imd = imd[['LSOA code (2011)', imd_col]] # Adjust column name if needed
    imd.columns = ['lsoa21cd', 'Income_Score']
    
    lookup = pd.read_csv(os.path.join(DATA_DIR, "lookup.csv"), dtype=str)
    lsoa_map = lookup[['lsoa21cd', 'msoa21cd', 'ladnm']].drop_duplicates()
    
    imd_msoa = imd.merge(lsoa_map, on='lsoa21cd').groupby(['msoa21cd', 'ladnm'])['Income_Score'].mean().reset_index()
    
    thresh_10 = imd_msoa['Income_Score'].quantile(0.90)
    top_10 = imd_msoa[imd_msoa['Income_Score'] >= thresh_10]
    
    print(f"Top 10% Threshold: {thresh_10:.3f}")
    print(f"Number of Top 10% MSOAs: {len(top_10)}")
    
    print("\nBorough Breakdown of Top 10%:")
    print(top_10['ladnm'].value_counts())
    
    health_files = glob.glob(os.path.join(DATA_DIR, "health_*.csv"))
    copd_vals = []
    for f in health_files:
        try:
            df = pd.read_csv(f)
            df = df[df["Indicator Name"].str.contains("COPD", case=False, na=False)]
            df = df[['Area Code', 'Value']]
            copd_vals.append(df)
        except: pass
    copd = pd.concat(copd_vals)
    copd.columns = ['msoa21cd', 'Baseline_COPD']
    
    top_10_health = top_10.merge(copd, on='msoa21cd')
    other_health = imd_msoa[imd_msoa['Income_Score'] < thresh_10].merge(copd, on='msoa21cd')
    
    print(f"\nMean Baseline COPD (Top 10%): {top_10_health['Baseline_COPD'].mean():.2f}")
    print(f"Mean Baseline COPD (Rest): {other_health['Baseline_COPD'].mean():.2f}")
    
    with open(os.path.join(OUTPUT_DIR, "anomaly_investigation.txt"), "w") as f:
        f.write("--- Top 10% Analysis ---\n")
        f.write(f"Threshold: {thresh_10:.3f}\n")
        f.write(f"Boroughs:\n{top_10['ladnm'].value_counts()}\n")
        f.write(f"Mean Baseline COPD (Top 10%): {top_10_health['Baseline_COPD'].mean():.2f}\n")
        f.write(f"Mean Baseline COPD (Rest): {other_health['Baseline_COPD'].mean():.2f}\n")

if __name__ == "__main__":
    investigate()