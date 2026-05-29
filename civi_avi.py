import os
import glob
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

all_cleaned_data = []

file_paths = glob.glob(r"D:\Python\project\civil_aviation\*.xlsx")

for file_path in file_paths:
    filename = os.path.basename(file_path)
    
    try:
        time_period = filename.split(",")[1].replace(".xlsx", "").replace("(2)", "").strip()
    except IndexError:
        time_period = "Unknown Period"
        
    print(f"Running logic on: {filename} ...")

    # ==========================================
    # ==========================================
    df = pd.read_excel(file_path, skiprows = 2)

    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.lower()

    mask = ~df.astype(str).apply(lambda row: row.str.contains('SUB TOTAL|^TOTAL$', case=False).any(), axis=1)
    df = df[mask]

    if "s.no." in df.columns:
        df.drop("s.no.", axis=1, inplace = True)

    df['OD Pair'] = df['city 1'] + "-" + df['city 2']

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
    # ==========================================

    df_final['time_period'] = time_period
    
    all_cleaned_data.append(df_final)

master_df = pd.concat(all_cleaned_data, ignore_index=True)


# ==========================================
# ==========================================

output_folder = r"D:\Python\project\civil_aviation\clean_data"

os.makedirs(output_folder, exist_ok=True)

output_file_path = os.path.join(output_folder, "Master_Civil_Aviation_Data.xlsx")

master_df.to_excel(output_file_path, index=False)

print(f"\nSuccess! All files processed.")
print(f"Master dataset saved to: {output_file_path}")
