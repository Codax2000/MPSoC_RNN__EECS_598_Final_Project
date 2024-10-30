# plan: 
# 2,3,7,11,14,6,5,10,9,12 as input, try to predict 13
# Using Time since the epoch, to match the rows. If there is no exact match take the minimum time difference
# column that we care about:  
    # 9. Ambient Temperature [°C]
    # 10. Surface Temperature [°C]
    # 11. Solar Radiation [W/m^2]
    # 12. Relative Humidity [%]
    # 13. Soil Moisture [%]
    # 14. Watermark [kPa]
    # 15. Rain Meter [mm]
    # 16. Wind Speed [m/s]
    # 17. Wind Direction [°]


import os
import pandas as pd
from glob import glob

# Define the files to read
file_numbers = [2, 3, 11, 14, 6, 5, 10, 9, 12, 13]
file_paths = [f"python_scripts\\MLmodel\\Dataset\\stbernard-meteo-{num}.txt" for num in file_numbers]

# Define the columns we want to keep (Python indices start at 0, so subtract 1 from each column index)
columns_to_keep   = ['TimeEpoch', 'AmbientTemp', 'SurfaceTemp', 'SolarRadiation', 'RelHumidity',
                   'SoilMoisture', 'Watermark', 'RainMeter', 'WindSpeed', 'WindDirection']
  # Only necessary columns, modify as needed
time_column = 7  # Column 8 in original data (Time since epoch)

# Load each file into a dictionary of DataFrames with only relevant columns
data_frames = {}
for path in file_paths:
    try:
        # Attempt to read the file
        df = pd.read_csv(path, delim_whitespace=True, header=None)
        df.fillna(0, inplace=True)

        # Rename columns for easy access
        df.columns = ['StationID', 'Year', 'Month', 'Day', 'Hour', 'Minute', 'Second', 'TimeEpoch', 
                      'AmbientTemp', 'SurfaceTemp', 'SolarRadiation', 'RelHumidity', 'SoilMoisture', 
                      'Watermark', 'RainMeter', 'WindSpeed', 'WindDirection']
        
        # Keep only the columns we need
        df = df[columns_to_keep]

        # Sort by TimeEpoch for merging
        df = df.sort_values(by='TimeEpoch').reset_index(drop=True)
        data_frames[path] = df
        print(f"{path} TimeEpoch range: {df['TimeEpoch'].min()} - {df['TimeEpoch'].max()}")
        # print(df)

    except Exception as e:
        print(f"Error loading {path}: {e}")

# Ensure we have data to merge
if not data_frames:
    print("No valid files were loaded. Please check the file contents.")
else:
    # Start merging with the first file
    merged_df = list(data_frames.values())[0]
    for path, df in list(data_frames.items())[1:]:
        # Merge on TimeEpoch with specified suffixes to avoid duplicate columns
        merged_df = pd.merge_asof(
            merged_df, df,
            on='TimeEpoch', direction='nearest', tolerance=60,
            suffixes=('', f'_{path.split("-")[-1].split(".")[0]}')  # Unique suffix for each file number
        )

    # Drop rows with NaN values resulting from unmatched times
    merged_df.dropna(inplace=True)

    # Write to a new file
    output_file = "merged_stbernard_meteo.txt"
    merged_df.to_csv(output_file, sep='\t', index=False)
    print(f"Data successfully merged into {output_file}")

