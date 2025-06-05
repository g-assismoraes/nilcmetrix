# -*- coding: utf-8 -*-
import os, json, text_metrics

# ─────────────────────────────────────────────────────────────
# 1 · ARQUIVOS
# ─────────────────────────────────────────────────────────────
INPUT_JSON  = "essayModels.json" 
OUTPUT_JSON = "llms_metrics.json"

# ─────────────────────────────────────────────────────────────
# 2 · CARREGAR DADOS DE ENTRADA
# ─────────────────────────────────────────────────────────────
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)                      # ano → arquivo.txt → texto

# ─────────────────────────────────────────────────────────────
# 3 · CARREGAR (OU CRIAR) DICIONÁRIO DE SAÍDA INCREMENTAL
# ─────────────────────────────────────────────────────────────
if os.path.isfile(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        output = json.load(f)
else:
    output = {}

# ─────────────────────────────────────────────────────────────
# 4 · FUNÇÃO AUXILIAR PARA SALVAR A CADA ITERAÇÃO
# ─────────────────────────────────────────────────────────────
def salvar_parcial():
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────
# 5 · LOOP PRINCIPAL
# ─────────────────────────────────────────────────────────────
total_novas = 0

for year, year_block in data.items():
    for filename, raw_text in year_block.items():

        if filename == "Numero de redacoes":   # pula metadado numérico
            continue
        if not isinstance(raw_text, str) or not raw_text.strip():
            continue                           # pula textos vazios

        # ID único: "2013_gpt4o_temp03"
        text_id = f"{year}_{filename.rsplit('.', 1)[0]}".lower()

        # Evita recalcular o que já está salvo
        if text_id in output:
            continue

        # ── 5.1 · PRE-PROCESSAMENTO ──────────────────────────
        processed = (raw_text.replace('{{quotes}}',   '"')
                              .replace('{{exclamation}}', '!')
                              .replace('{{enter}}',  '\n')
                              .replace('{{sharp}}',  '#')
                              .replace('{{ampersand}}', '&')
                              .replace('{{percent}}', '%')
                              .replace('{{dollar}}',  '$')
                              .encode("utf-8", "surrogateescape")
                              .decode("utf-8"))

        # ── 5.2 · MÉTRICAS ───────────────────────────────────
        t       = text_metrics.Text(processed)
        metrics = text_metrics.nilc_metrics.values_for_text(t).as_flat_dict()

        # ── 5.3 · ATUALIZA SAÍDA E SALVA PARCIAL ─────────────
        output[text_id] = {
            "year"    : year,
            "file"    : filename,
            "metrics" : metrics,
            "text"    : processed
        }
        salvar_parcial()
        total_novas += 1
        print(f"{text_id} processado e salvo.")

print(f"\nConcluído: {total_novas} novas redações adicionadas a {OUTPUT_JSON}.")
