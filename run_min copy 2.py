# -*- coding: utf-8 -*-
import text_metrics
import sys
import json



text = "ouviram do ipiranga, as margens plácidas, o grito retumbante de um povo heróico. eles são legais."
raw = text.replace('{{quotes}}', '"')
raw = raw.replace('{{exclamation}}', '!')
raw = raw.replace('{{enter}}', '\n')
raw = raw.replace('{{sharp}}', '#')
raw = raw.replace('{{ampersand}}', '&')
raw = raw.replace('{{percent}}', '%')
raw = raw.replace('{{dollar}}', '$')

print(raw)
raw = raw.encode("utf-8", "surrogateescape").decode("utf-8")
t = text_metrics.Text(raw)
ret = text_metrics.nilc_metrics.values_for_text(t).as_flat_dict()

result = '' 
for f in ret:
    m = "%s:%s," % (f, ret[f])
    #print(m)
    result += m
print("++", result, "++")

file_path = 'file.json'

# Save the dictionary as a JSON file
with open(file_path, 'w') as f:
    json.dump(ret, f, indent=4)
