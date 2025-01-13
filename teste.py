import pandas as pd
import json
#import text_metrics

# Path to the CSV
csv_file_path = 'aida.csv'
output_file_path = 'mistral_metrics_output.json'

# Read the CSV into a DataFrame
df = pd.read_csv(csv_file_path)

df = df[df['generator_model'] == 'mistral-7b']

print(len(df))

# Initialize an output dictionary
output_dict = {}

# Loop through each row in the DataFrame
i = 0
for idx, row in df.iterrows():
    # Retrieve the row's ID and text
    text_id = str(row['id'])      # convert to string if needed
    raw_text = row['generated_text'] #generated_text for model text analise for human text
    
    
    if pd.isna(raw_text):
        print(text_id)
        