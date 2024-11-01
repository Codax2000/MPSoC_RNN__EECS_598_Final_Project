def split_file(filename, prefix, rows_per_chunk=30):
    with open(filename, 'r') as file:
        lines = file.readlines()
        
    num_chunks = (len(lines) + rows_per_chunk - 1) // rows_per_chunk
    
    for i in range(num_chunks):
        start = i * rows_per_chunk
        end = start + rows_per_chunk
        chunk = lines[start:end]
        
        with open(f"{prefix}_{i + 1}.txt", 'w') as new_file:
            new_file.writelines(chunk)


inFolder = 'python_scripts\\MLmodel\\Dataset\\'
outFolder = 'python_scripts\\MLmodel\\Dataset\\Split\\'

# Splitting df_test_data.txt
split_file(inFolder + 'df_test_data.txt', outFolder + 'df_test_data')
# Splitting df_test_key.txt
split_file(inFolder + 'df_test_key.txt', outFolder + 'df_test_key')
# Splitting df_test_data.txt
split_file(inFolder + 'df_train_data.txt', outFolder + 'df_train_data')
# Splitting df_test_key.txt
split_file(inFolder + 'df_train_key.txt', outFolder + 'df_train_key')
# Splitting df_test_data.txt
split_file(inFolder + 'df_val_data.txt', outFolder + 'df_val_data')
# Splitting df_test_key.txt
split_file(inFolder + 'df_val_key.txt', outFolder + 'df_val_key')