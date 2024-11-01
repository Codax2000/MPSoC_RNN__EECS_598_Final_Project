import pandas as pd
# path = "python_scripts\\MLmodel\\Dataset\\Split\\test_data\\df_test_data_1.txt"
path = "python_scripts\\MLmodel\\Dataset\\df_test_data.txt"
df = pd.read_csv(path, delim_whitespace=True, header=None)
print(df.columns)