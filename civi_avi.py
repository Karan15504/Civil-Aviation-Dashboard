import os
import glob
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# List to hold the cleaned data from every file
all_cleaned_data = []

# Find all Excel files in the civil_aviation folder
file_paths = glob.glob(r"D:\Python\project\civil_aviation\*.xlsx")

# Exclude the distance reference excel file from the flight data files list
file_paths = [f for f in file_paths if "CIVIL AVIATION DISTANCE.xlsx" not in os.path.basename(f)]


for file_path in file_paths:
    # Extract the filename
    filename = os.path.basename(file_path)
    
    # Extract time period from the filename
    try:
        # Splits by comma, removes .xlsx and (2), leaving e.g., "JANUARY 2026"
        time_period = filename.split(",")[1].replace(".xlsx", "").replace("(2)", "").strip()
    except IndexError:
        time_period = "Unknown Period"
        
    print(f"Running logic on: {filename} ...")

    # ==========================================
    # YOUR EXACT LOGIC STARTS HERE
    # ==========================================
    df = pd.read_excel(file_path, skiprows = 2)

    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()

    # Clean leading/trailing spaces from city columns to prevent join mismatches
    df['city 1'] = df['city 1'].astype(str).str.strip()
    df['city 2'] = df['city 2'].astype(str).str.strip()


    mask = ~df.astype(str).apply(lambda row: row.str.contains('SUB TOTAL|^TOTAL$', case=False).any(), axis=1)
    df = df[mask]

    # Quick check just in case a future file doesn't have the s.no. column
    if "s.no." in df.columns:
        df.drop("s.no.", axis=1, inplace = True)

    df['OD Pair'] = df['city 1'] + "-" + df['city 2']

    # .fillna(0) added to safely handle any blank cells before converting to integer
    df["passengers \nto city 2"] = df["passengers \nto city 2"].replace("-",0).fillna(0)
    df["passengers \nto city 2"] = df["passengers \nto city 2"].astype(int)

    df["passengers \nfrom city 2"] = df["passengers \nfrom city 2"].replace("-",0).fillna(0)
    df["passengers \nfrom city 2"] = df["passengers \nfrom city 2"].astype(int)

    df["freight \nto city 2"] = df["freight \nto city 2"].replace("-",0).fillna(0)
    df["freight \nfrom city 2"] = df["freight \nfrom city 2"].replace("-",0).fillna(0)

    df["mail \nto city 2"] = df["mail \nto city 2"].replace("-",0).fillna(0)
    df["mail \nfrom city 2"] = df["mail \nfrom city 2"].replace("-",0).fillna(0)

    df = df.sort_values(by =("OD Pair"))

    df["OD pair2"] = df["city 2"] + "-" + df["city 1"]

    df[['city3', 'city4']] = df['OD pair2'].str.split('-', expand=True)

    df1 = df[["OD Pair", "city 1","city 2" , "passengers \nto city 2" , "freight \nto city 2" , "mail \nto city 2"]]

    df2 = df[["OD pair2","city3", "city4", "passengers \nfrom city 2", "freight \nfrom city 2" ,"mail \nfrom city 2"]]

    df1.columns = ["OD PAIRS", "city 1" , "city2", "passengers" , "freight", "mail"]

    df2.columns = ["OD PAIRS", "city 1" , "city2", "passengers" , "freight", "mail"]

    df_final = pd.concat([df1,df2], axis= 0)

    df_final = df_final.melt(
        id_vars=df_final.columns[:3],
        value_vars=df_final.columns[3:],
        var_name='type',
        value_name='value'
    )

    df_final = df_final.sort_values(by=["OD PAIRS"])
    # ==========================================
    # YOUR EXACT LOGIC ENDS HERE
    # ==========================================

    # Add the time period column for this specific file
    df_final['time_period'] = time_period
    
    # Add this file's cleaned dataframe to our master list
    all_cleaned_data.append(df_final)

# Combine all the individual dataframes into one massive dataframe
master_df = pd.concat(all_cleaned_data, ignore_index=True)

# Load the distance lookup Excel file
distance_file_path = r"D:\Python\project\civil_aviation\CIVIL AVIATION DISTANCE.xlsx"
print(f"\nLoading distance reference data: {os.path.basename(distance_file_path)} ...")
dist_df = pd.read_excel(distance_file_path)

# Clean and deduplicate the distance lookup data to prevent duplicate merge results
dist_df['SECTION'] = dist_df['SECTION'].astype(str).str.strip()
dist_df = dist_df.drop_duplicates(subset=['SECTION'], keep='first')

# Join the distance columns to the master dataframe
print("Merging distance data into master dataset...")
master_df = master_df.merge(dist_df, left_on='OD PAIRS', right_on='SECTION', how='left')

# Drop the redundant 'SECTION' column from the merge
if 'SECTION' in master_df.columns:
    master_df.drop('SECTION', axis=1, inplace=True)

# Remove all duplicate rows from the final master dataframe
print("Removing all duplicate rows from the final dataset...")
master_df = master_df.drop_duplicates()

# ==========================================

output_folder = r"D:\Python\project\civil_aviation\clean_data"

os.makedirs(output_folder, exist_ok=True)

output_file_path = os.path.join(output_folder, "Master_Civil_Aviation_Data.xlsx")

try:
    master_df.to_excel(output_file_path, index=False)
    print(f"\nSuccess! All files processed.")
    print(f"Master dataset saved to: {output_file_path}")
except PermissionError:
    import time
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    alternative_file_path = os.path.join(output_folder, f"Master_Civil_Aviation_Data_{timestamp}.xlsx")
    print(f"\n[WARNING] Permission denied: '{output_file_path}' seems to be open in Excel.")
    print(f"Please close the file in Excel and run the script again.")
    print(f"Saving a backup copy of the cleaned data to: {alternative_file_path}")
    master_df.to_excel(alternative_file_path, index=False)

