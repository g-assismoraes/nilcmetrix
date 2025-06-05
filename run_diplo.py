# -*- coding: utf-8 -*-
import json
import text_metrics           # mantém sua biblioteca de métricas

# ─────────────────────────────────────────────────────────────
# 1 · ARQUIVOS DE ENTRADA E SAÍDA
# ─────────────────────────────────────────────────────────────
INPUT_JSON_PATH  = "essayCandidates.json"          # novo arquivo de entrada
OUTPUT_JSON_PATH = "candidates_metrics.json"  # saída com métricas

# ─────────────────────────────────────────────────────────────
# 2 · CARREGAR O JSON
# ─────────────────────────────────────────────────────────────
with open(INPUT_JSON_PATH, "r", encoding="utf-8") as f:
    data = json.load(f)        # estrutura aninhada por ano → candidato → texto

# ─────────────────────────────────────────────────────────────
# 3 · ITERAR PELOS ANOS E CANDIDATOS
# ─────────────────────────────────────────────────────────────
output_dict = {}

for year, year_data in data.items():
    for candidate, raw_text in year_data.items():
        # pula a chave "Numero de redacoes"
        if candidate == "Numero de redacoes":
            continue
        if not isinstance(raw_text, str) or not raw_text.strip():
            continue           # garante que só textos válidos entrem

        # gera um ID único: ex. "2013_filipe_brum_cunha"
        text_id = f"{year}_{candidate.replace(' ', '_').lower()}"

        # ── 3.1 · PRE-PROCESSAMENTO – mesmos replaces de antes
        processed = (raw_text.replace('{{quotes}}',   '"')
                              .replace('{{exclamation}}', '!')
                              .replace('{{enter}}',  '\n')
                              .replace('{{sharp}}',  '#')
                              .replace('{{ampersand}}', '&')
                              .replace('{{percent}}', '%')
                              .replace('{{dollar}}',  '$')
                              .encode("utf-8", "surrogateescape")
                              .decode("utf-8"))

        # ── 3.2 · CÁLCULO DAS MÉTRICAS
        t        = text_metrics.Text(processed)
        metrics  = text_metrics.nilc_metrics.values_for_text(t).as_flat_dict()

        # ── 3.3 · ARMAZENAR NO DICIONÁRIO DE SAÍDA
        output_dict[text_id] = {
            "year"     : year,
            "candidate": candidate,
            "text"     : processed,
            "metrics"  : metrics,
        }

# ─────────────────────────────────────────────────────────────
# 4 · SALVAR O RESULTADO
# ─────────────────────────────────────────────────────────────
with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(output_dict, f, indent=4, ensure_ascii=False)

print(f"Métricas salvas em {OUTPUT_JSON_PATH}")
