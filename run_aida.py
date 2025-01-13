# -*- coding: utf-8 -*-
import pandas as pd
import json
import text_metrics

# Path to the CSV
csv_file_path = 'aida.csv'
output_file_path = 'gemma_metrics_output.json'

# Read the CSV into a DataFrame
df = pd.read_csv(csv_file_path)

df = df[df['generator_model'] == 'gemma2-9b']

print(len(df))

# Initialize an output dictionary
output_dict = {}

# Loop through each row in the DataFrame
for idx, row in df.iterrows():
    # Retrieve the row's ID and text
    text_id = str(row['id'])      # convert to string if needed
    raw_text = row['generated_text'] #generated_text for model text analise for human text
    
    if pd.isna(raw_text):
        continue
    

    # Preprocess the text (perform the same replacements)
    raw_text = raw_text.replace('{{quotes}}', '"')
    raw_text = raw_text.replace('{{exclamation}}', '!')
    raw_text = raw_text.replace('{{enter}}', '\n')
    raw_text = raw_text.replace('{{sharp}}', '#')
    raw_text = raw_text.replace('{{ampersand}}', '&')
    raw_text = raw_text.replace('{{percent}}', '%')
    raw_text = raw_text.replace('{{dollar}}', '$')

    # Encoding and decoding for proper text handling
    raw_text = raw_text.encode("utf-8", "surrogateescape").decode("utf-8")

    # Process text using text_metrics
    t = text_metrics.Text(raw_text)
    ret = text_metrics.nilc_metrics.values_for_text(t).as_flat_dict()

    # Store the metrics and processed text in the output dictionary
    output_dict[text_id] = {
        'metrics': ret,
        'text': raw_text
    }

# Output final result
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(output_dict, f, indent=4, ensure_ascii=False)

print(f"Metrics saved to {output_file_path}")
