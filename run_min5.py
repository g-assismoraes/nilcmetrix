# -*- coding: utf-8 -*-
import text_metrics
import sys
import json

# Load JSON data from a file
file_path = 'opt_lora.json'
with open(file_path, 'r') as f:
    data = json.load(f)

# Choose either "generated" or "label" to use for processing
text_type = "generated"  # Change to "label" as needed

# Number of items to process
number_of_items = 100  # Change this number to process more or fewer items

# Initialize an output dictionary
output_dict = {}

# Process only the first 'number_of_items' from the JSON data
for key, value in list(data.items())[:number_of_items]:
    text = value[text_type]
    ret = {}
    if text.strip():
        text_to_save = text.encode("utf-8", "surrogateescape").decode("utf-8")
        raw = text.replace('{{quotes}}', '"')
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

    # Add the processed text and its metrics to the output dictionary with the same original key
    output_dict[key] = {
        'text': text_to_save,
        'metrics': ret
    }

# Output final result
output_file_path = 'nilc_opt-lora.json'
with open(output_file_path, 'w') as f:
    json.dump(output_dict, f, indent=4)