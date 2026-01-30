import pandas as pd
import os

DATA_DIR = os.path.join("01_Data", "Processed_Data")

def clean_energy_data():
    df = pd.read_csv(os.path.join(DATA_DIR, "energy_prices_processed.csv"), skiprows=8)
    
    df = df.iloc[1:] # Drop the code row (D7DW, etc.)
    df = df[['Year and dataset code row', 'Month', 'Current price indices: Gas ', 'Current price indices: Electricity ']]
    df.columns = ['Year', 'Month', 'Gas_Index', 'Electricity_Index']
    
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    df = df[(df['Year'] >= 2015) & (df['Year'] <= 2024)]
    
    month_map = {
        'January': 1, 'February': 2, 'March': 3, 'April': 4,
        'May': 5, 'June': 6, 'July': 7, 'August': 8,
        'September': 9, 'October': 10, 'November': 11, 'December': 12
    }
    df['Month_Num'] = df['Month'].map(month_map)
    
    df['Gas_Index'] = pd.to_numeric(df['Gas_Index'], errors='coerce')
    df['Electricity_Index'] = pd.to_numeric(df['Electricity_Index'], errors='coerce')
    
    df['Date'] = df['Year'].astype(str) + '-' + df['Month_Num'].astype(str).str.zfill(2) + '-01'
    
    df.to_csv(os.path.join(DATA_DIR, "energy_prices_final.csv"), index=False)
    print("Saved energy_prices_final.csv")

if __name__ == "__main__":
    clean_energy_data()