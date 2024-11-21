import os
import pandas as pd
from glob import glob
import numpy as np

# Define the files to read
file_numbers = [2, 3, 7, 11, 14, 6, 5, 10, 9, 12, 13]
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

# normalize data to [-1, 1]
def normalize_column(col):
    max_val = col.max()
    min_val = col.min()
    if min_val == max_val:
        return col.apply(lambda x: 0)
    else:
        return 2 * (col - min_val) / (max_val - min_val) - 1

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
    merged_df = merged_df.apply(normalize_column) #normalize each col

    # Write to a new file
    output_file = "python_scripts\\MLmodel\\Dataset\\merged_stbernard_meteo.txt" #9553 data entries
    # merged_df.to_csv(output_file, sep='\t', index=False)
    print(f"Data successfully merged into {output_file}")


# Load the tab-separated file with headers
df = merged_df

# Define the list of column headers to be extracted
columns_to_extract = ['AmbientTemp_13']
columns_to_delete = ['TimeEpoch','AmbientTemp_13', 'SurfaceTemp_13', 'SolarRadiation_13', 'RelHumidity_13',
    'SoilMoisture_13', 'Watermark_13', 'RainMeter_13', 'WindSpeed_13', 'WindDirection_13']
    

# Separate the dataframe into two: one with the specified columns, and one with the remaining columns

df_extracted = df[columns_to_extract]
df_extracted = df_extracted[1:]
df_remaining = df.drop(columns = columns_to_delete)
de_remaining = de_remaining[1:]

df_remaining.to_csv('python_scripts\\MLmodel\\Dataset\\all_data\\data.txt', sep=',', index=False)
df_extracted.to_csv('python_scripts\\MLmodel\\Dataset\\all_key\\key.txt', sep=',', index=False)


def split_file(filename_data, filename_key, prefix_list, rows_per_chunk=30):
    with open(filename_data, 'r') as file:
        lines = file.readlines()

    with open(filename_key, 'r') as file:
        lines_key = file.readlines()
        
    # lines = lines[1:]
    # lines_key = lines_key[1:]
    num_chunks = (len(lines) + rows_per_chunk - 1) // rows_per_chunk

    splitList = np.array([0,0,0,0,0,0,0,0,1,2])
    
    for i in range(num_chunks-1): #only keep rows with 30
        if i%10 == 0:
            np.random.shuffle(splitList)
        start = i * rows_per_chunk
        end = start + rows_per_chunk
        chunk_data = lines[start:end]
        chunk_key = lines_key[start:end]

        with open(f"{prefix_list[splitList[i%10]][0]}_{i + 1}.txt", 'w') as new_file:
            new_file.writelines(chunk_data)
        with open(f"{prefix_list[splitList[i%10]][1]}_{i + 1}.txt", 'w') as new_file:
            new_file.writelines(chunk_key)


inFolder = 'python_scripts\\MLmodel\\Dataset\\'
outFolder = 'python_scripts\\MLmodel\\Dataset\\Split\\'
prefix_list = [[outFolder + 'train_data\\df_train_data', outFolder + 'train_key\\df_train_key'],
               [outFolder + 'test_data\\df_test_data', outFolder + 'test_key\\df_test_key'],
               [outFolder + 'val_data\\df_val_data', outFolder + 'val_key\\df_val_key']]

split_file(inFolder + 'all_data\\data.txt', inFolder + 'all_key\\key.txt', prefix_list)

print("done")
