# -*- coding: utf-8 -*-
import os
import json
import text_metrics

# Caminho para o diretório com os arquivos JSON
input_dir = 'fauna/pira/'  
output_dir = 'fauna_output/'  
os.makedirs(output_dir, exist_ok=True)

# ===>> Defina aqui a chave que contém o texto (ex: "generated", "original")
TEXT_KEY = 'reference'  

ID_KEY = 'id'  # se não existir, será gerado automaticamente

# Função de pré-processamento
def preprocess_text(text):
    if not text:
        return None
    text = text.replace('{{quotes}}', '"')
    text = text.replace('{{exclamation}}', '!')
    text = text.replace('{{enter}}', '\n')
    text = text.replace('{{sharp}}', '#')
    text = text.replace('{{ampersand}}', '&')
    text = text.replace('{{percent}}', '%')
    text = text.replace('{{dollar}}', '$')
    return text.encode("utf-8", "surrogateescape").decode("utf-8")

# Processa cada JSON no diretório
for filename in os.listdir(input_dir):
    if not filename.endswith('.json'):
        continue

    input_path = os.path.join(input_dir, filename)
    output_filename = filename.replace('.json', f'_metrics_{TEXT_KEY}.json')
    output_path = os.path.join(output_dir, output_filename)

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print(f"⚠️  Ignorado (esperava uma lista): {filename}")
        continue

    metrics_output = {}

    for idx, item in enumerate(data):
        # Usa o campo ID se existir, senão gera um
        if ID_KEY in item:
            text_id = str(item[ID_KEY])
        else:
            text_id = f"{filename.replace('.json', '')}_{idx:05d}"

        raw_text = item.get(TEXT_KEY)
        if not raw_text:
            continue

        processed_text = preprocess_text(raw_text)
        if not processed_text:
            continue

        # Calcula métricas
        t = text_metrics.Text(processed_text)
        ret = text_metrics.nilc_metrics.values_for_text(t).as_flat_dict()

        # Armazena resultado
        metrics_output[text_id] = {
            'metrics': ret,
            'text': processed_text
        }

    # Salva o resultado
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(metrics_output, f, indent=4, ensure_ascii=False)

    print(f"✅ Processado: {filename} → {output_filename}")