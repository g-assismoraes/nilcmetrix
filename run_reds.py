# -*- coding: utf-8 -*-
import os
import json
import text_metrics

# Directory containing .txt files
directory_path = 'reds'

# Initialize an output dictionary
output_dict = {}

# Loop through each file in the directory
for filename in os.listdir(directory_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(directory_path, filename)
        
        # Read the content of the .txt file
        with open(file_path, 'r', encoding='utf-8') as f:
            raw = f.read()
        
        # Preprocess the text
        raw = raw.replace('{{quotes}}', '"')
        raw = raw.replace('{{exclamation}}', '!')
        raw = raw.replace('{{enter}}', '\n')
        raw = raw.replace('{{sharp}}', '#')
        raw = raw.replace('{{ampersand}}', '&')
        raw = raw.replace('{{percent}}', '%')
        raw = raw.replace('{{dollar}}', '$')

        # Encoding and decoding for proper text handling
        raw = raw.encode("utf-8", "surrogateescape").decode("utf-8")
        
        # Process text using text_metrics
        t = text_metrics.Text(raw)
        ret = text_metrics.nilc_metrics.values_for_text(t).as_flat_dict()

        # Add the processed text and its metrics to the output dictionary
        output_dict[filename] = {
            'metrics': ret,
            'text': raw,
        }

# Output final result
output_file_path = 'metrics_output.json'
with open(output_file_path, 'w', encoding='utf-8') as f:
    json.dump(output_dict, f, indent=4, ensure_ascii=False)
