# -*- coding: utf-8 -*-
import os, json, ast, text_metrics

# ─────────────────────────────────────────────────────────────
# 1 · ARQUIVOS
# ─────────────────────────────────────────────────────────────
INPUT_JSON  = "essayENEM.json" 
OUTPUT_JSON = "enem_metrics.json"

# ─────────────────────────────────────────────────────────────
# 2 · CARREGAR DADOS DE ENTRADA
# ─────────────────────────────────────────────────────────────
with open(INPUT_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)                      # {"Texto1": "['...', '...']", ...}

# ─────────────────────────────────────────────────────────────
# 3 · CARREGAR (OU CRIAR) SAÍDA INCREMENTAL
# ─────────────────────────────────────────────────────────────
if os.path.isfile(OUTPUT_JSON):
    with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
        output = json.load(f)
else:
    output = {}

def salvar_parcial():
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)

# ─────────────────────────────────────────────────────────────
# 4 · LOOP PRINCIPAL
# ─────────────────────────────────────────────────────────────
novos = 0

for label, raw_value in data.items():

    text_id = label.lower()                 # "texto1", "texto2"…
    if text_id in output:
        continue                            # já processado

    # ------------------------------------------------------------------
    # 4.1 · STRING  →  LISTA  →  TEXTO ÚNICO
    # ------------------------------------------------------------------
    try:
        parts = ast.literal_eval(raw_value)          # ['parágrafo 1', ...]
        if not isinstance(parts, list):
            parts = [raw_value]
    except Exception:
        parts = [raw_value]

    # junta com espaçamento duplo entre parágrafos
    joined = "\n\n".join(p.strip() for p in parts)


    processed = joined.replace("[", "").replace("]", "")

    processed = (processed.replace('{{quotes}}', '"')
                           .replace('{{exclamation}}', '!')
                           .replace('{{enter}}', '\n')
                           .replace('{{sharp}}', '#')
                           .replace('{{ampersand}}', '&')
                           .replace('{{percent}}', '%')
                           .replace('{{dollar}}', '$')
                           .encode("utf-8", "surrogateescape")
                           .decode("utf-8"))

    # ------------------------------------------------------------------
    # 4.2 · MÉTRICAS
    # ------------------------------------------------------------------
    t       = text_metrics.Text(processed)
    metrics = text_metrics.nilc_metrics.values_for_text(t).as_flat_dict()

    # ------------------------------------------------------------------
    # 4.3 · ATUALIZA SAÍDA + SALVA
    # ------------------------------------------------------------------
    output[text_id] = {
        "source"   : label,      # preserva exatamente como veio
        "metrics" : metrics,
        "text"    : processed
    }
    salvar_parcial()
    novos += 1
    print(f"{label} processado e salvo.")

print(f"\nConcluído: {novos} novos textos adicionados a {OUTPUT_JSON}.")
