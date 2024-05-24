#consolidator
import os
import pandas as pd

current_directory = os.getcwd()
print(current_directory)
merged_data = pd.DataFrame()
temp = []

for filename in os.listdir(current_directory):
    if ((filename.endswith(".xlsx"))):
        file_path = os.path.join(current_directory, filename)
        team = filename.replace(".xlsx","")
        data = pd.read_excel(file_path)
        data = data.drop_duplicates()
        data['League'] = team
        data['Period'] = 'April 2024'
        temp.append(data)
        merged_data = pd.concat(temp, ignore_index=True)

merged_data.to_excel('apr_2024.xlsx', index=False)
merged_data