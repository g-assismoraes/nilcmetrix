import json
import math
import os

# Function to load JSON data
def load_json(file_path):
     with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

# Function to find min and max values for each metric across all data
def find_min_max_metrics(all_data):
    metrics_min_max = {}
    for _, data in all_data.items():
        for _, entry in data.items():
            if not entry['metrics']:  # Skip empty metrics
                continue
            for metric, value in entry['metrics'].items():
                if metric not in metrics_min_max:
                    metrics_min_max[metric] = {"min": float('inf'), "max": float('-inf')}
                metrics_min_max[metric]['min'] = min(metrics_min_max[metric]['min'], value)
                metrics_min_max[metric]['max'] = max(metrics_min_max[metric]['max'], value)
    return metrics_min_max

# Function to normalize metrics data
def normalize_data(all_data, metrics_min_max):
    for file, data in all_data.items():
        for _, entry in data.items():
            if not entry['metrics']:  # Skip empty metrics
                continue
            for metric, value in entry['metrics'].items():
                if metric in metrics_min_max:  # Check in case metric was never found
                    min_val = metrics_min_max[metric]['min']
                    max_val = metrics_min_max[metric]['max']
                    if max_val != min_val:
                        normalized_value = (value - min_val) / (max_val - min_val)
                        entry['metrics'][metric] = normalized_value
                    else:
                        # If all values for this metric are the same, set to 0
                        entry['metrics'][metric] = 0.0

# Function to calculate Euclidean distance between two dictionaries of metrics
# restricted to a set of 'include_metrics' (if provided).
def euclidean_distance(metrics1, metrics2, include_metrics=None):
    if include_metrics is not None:
        # Only the specified metrics in both dicts
        common_keys = set(metrics1.keys()).intersection(metrics2.keys(), include_metrics)
    else:
        # Use all common keys if no subset is specified
        common_keys = set(metrics1.keys()).intersection(metrics2.keys())

    if not common_keys:
        return float('inf')  # Return infinite if no common metrics

    sum_squares = sum((metrics1[key] - metrics2[key])**2 for key in common_keys)
    return math.sqrt(sum_squares)

def compute_avg_std_for_group(reference_data, comparison_data, metrics_subset):
    """
    For the given group of metrics (metrics_subset),
    compute the average and std distance per model.
    
    Returns:
       average_distances: dict { model_filename: mean_distance }
       std_distances: dict { model_filename: std_distance }
    """

    # 1) Compute distances for each text key
    # Transformar a referência em lista ordenada de entradas
    reference_entries = list(reference_data.values())
    
    # Garantir que todos os modelos tenham o mesmo número de entradas
    num_entries = len(reference_entries)
    
    # Armazenar distâncias por modelo
    distances = {}

    for model_file, model_data in comparison_data.items():
        model_entries = list(model_data.values())
        
        if len(model_entries) != num_entries:
            print(f"[AVISO] Modelo {model_file} tem {len(model_entries)} entradas, esperado: {num_entries}")
            distances[model_file] = [float('inf')]
            continue

        for ref_entry, comp_entry in zip(reference_entries, model_entries):
            if not ref_entry['metrics'] or not comp_entry['metrics']:
                continue
            dist_val = euclidean_distance(
                ref_entry['metrics'],
                comp_entry['metrics'],
                metrics_subset
            )
            distances.setdefault(model_file, []).append(dist_val)

    # Calcular média e desvio padrão por modelo
    average_distances = {}
    std_distances = {}

    for model_file, dist_list in distances.items():
        if len(dist_list) > 0:
            mean_val = sum(dist_list) / len(dist_list)
            variance = sum((x - mean_val)**2 for x in dist_list) / len(dist_list)
            std_val = math.sqrt(variance)

            average_distances[model_file] = mean_val
            std_distances[model_file] = std_val
        else:
            average_distances[model_file] = float('inf')
            std_distances[model_file] = float('inf')

    return average_distances, std_distances


# ---- MAIN EXECUTION ----

# List of JSON filenames
json_filenames = [
    "gpt4o_recogna_reference.json", 
    #"bode_318B_recogna_r2_evaluate_percentiles_geeval_metrics_generated.json",
    # "boto_gemma_recogna_r2_evaluate_percentiles_geeval_metrics_generated.json",
    # "cabra_llama8b_recogna_r2_evaluate_percentiles_geeval_metrics_generated.json",
     "gpt4o_recogna_final_r2_evaluate_percentiles_geeval_metrics_generated.json",
    # "gptmini_recogna_final_r2_evaluate_percentiles_geeval_metrics_generated.json",
    # "piriquito_ollama_recogna_r2_evaluate_percentiles_geeval_metrics_generated.json",
    # "sabia_recogna_final_output_r2_evaluate_percentiles_geeval_metrics_generated.json",
    # "sabiazinho_recogna_final_output_r2_evaluate_percentiles_geeval_metrics_generated.json",
    #"tucano_recogna_r2_evaluate_percentiles_geeval_metrics_generated.json",
]

# 1) Load all JSON data
all_data = {f: load_json(f) for f in json_filenames}

# 2) Find min and max values for each metric
metrics_min_max = find_min_max_metrics(all_data)

# 3) Normalize the data
normalize_data(all_data, metrics_min_max)

# 4) Separate reference from comparison
reference_file = json_filenames[0]  # e.g. "nilc_reference.json"
reference_data = all_data[reference_file]
comparison_data = {f: data for f, data in all_data.items() if f != reference_file}

# Metric groups (edit these to your liking)
simplicidade = [
    "dialog_pronoun_ratio", "easy_conjunctions_ratio", "hard_conjunctions_ratio",
    "long_sentence_ratio", "medium_long_sentence_ratio", "medium_short_sentence_ratio",
    "short_sentence_ratio", "simple_word_ratio"
]

coesao_referencial = [
    "adjacent_refs", "anaphoric_refs", "adj_arg_ovl", "adj_cw_ovl", "adj_stem_ovl",
    "arg_ovl", "stem_ovl", "coreference_pronoun_ratio", "demonstrative_pronoun_ratio"
]

coesao_semantica = [
    "lsa_adj_mean", "lsa_adj_std", "lsa_all_mean", "lsa_all_std", "lsa_givenness_mean",
    "lsa_givenness_std", "lsa_paragraph_mean", "lsa_paragraph_std", "lsa_span_mean",
    "lsa_span_std", "cross_entropy"
]

complexidade_sintatica = [
    "words_before_main_verb", "adjunct_per_clause", "adverbs_before_main_verb_ratio",
    "apposition_per_clause", "clauses_per_sentence", "coordinate_conjunctions_per_clauses",
    "dep_distance", "frazier", "infinite_subordinate_clauses", "non_svo_ratio",
    "passive_ratio", "postponed_subject_ratio", "ratio_coordinate_conjunctions",
    "ratio_subordinate_conjunctions", "relative_clauses", "sentences_with_five_clauses",
    "sentences_with_four_clauses", "sentences_with_one_clause",
    "sentences_with_seven_more_clauses", "sentences_with_six_clauses",
    "sentences_with_three_clauses", "sentences_with_two_clauses",
    "sentences_with_zero_clause", "std_noun_phrase", "subordinate_clauses",
    "temporal_adjunct_ratio", "yngve"
]

leiturabilidade = ["brunet", "dalechall_adapted", "flesch", "gunning_fox", "honore"]

morfosintaxe = [
    "adjective_ratio", "adverbs", "content_words", "function_words", "noun_ratio",
    "pronoun_ratio", "verbs", "personal_pronouns", "adjectives_max", "adjectives_min",
    "adjectives_standard_deviation", "adverbs_diversity_ratio", "adverbs_max",
    "adverbs_min", "adverbs_standard_deviation", "indefinite_pronoun_ratio",
    "indicative_condition_ratio", "indicative_future_ratio", "infinitive_verbs",
    "inflected_verbs", "non-inflected_verbs", "nouns_max", "nouns_min",
    "nouns_standard_deviation", "oblique_pronouns_ratio", "prepositions_per_clause",
    "prepositions_per_sentence", "pronouns_max", "pronouns_min",
    "pronouns_standard_deviation", "punctuation_ratio", "ratio_function_to_content_words",
    "relative_pronouns_ratio", "second_person_possessive_pronouns", "second_person_pronouns",
    "third_person_possessive_pronouns", "third_person_pronouns", "verbs_max", "verbs_min",
    "verbs_standard_deviation", "first_person_possessive_pronouns", "first_person_pronouns"
]

info_semantica = [
    "adjectives_ambiguity", "adverbs_ambiguity", "nouns_ambiguity", "verbs_ambiguity",
    "hypernyms_verbs", "abstract_nouns_ratio", "content_words_ambiguity",
    "named_entity_ratio_sentence", "named_entity_ratio_text", "negative_words", "positive_words"
]

# Optionally, define all groups in a dictionary:
metric_groups = {
    "simplicidade": simplicidade,
    "coesao_referencial": coesao_referencial,
    "coesao_semantica": coesao_semantica,
    "complexidade_sintatica": complexidade_sintatica,
    "leiturabilidade": leiturabilidade,
    "morfosintaxe": morfosintaxe,
    "info_semantica": info_semantica
}

# Also define a "general" group if you want *all metrics combined*:
# (If you truly want every metric that has appeared, you could do:
#   set_of_all_metrics = set(m for data in all_data.values() for entry in data.values() for m in entry["metrics"].keys())
# )
all_groups_combined = []
for g_name, g_list in metric_groups.items():
    all_groups_combined.extend(g_list)
all_groups_combined = list(set(all_groups_combined))  # remove duplicates if any

metric_groups["all"] = all_groups_combined


# ----- Compute and store results -----
# We'll store the results in a nested dict like:
# results[group_name] = {
#     "average": { model: val, ... },
#     "std": { model: val, ... }
# }
results = {}

for group_name, group_metrics in metric_groups.items():
    avg_dist, std_dist = compute_avg_std_for_group(
        reference_data,
        comparison_data,
        group_metrics
    )
    results[group_name] = {
        "average": avg_dist,
        "std": std_dist
    }

# ----- Write results to text file -----
with open("model_distances.txt", "w") as txt_file:
    txt_file.write(f"Distances to Reference: {reference_file}\n\n")

    for group_name in results:
        txt_file.write(f"--- Metric Group: {group_name} ---\n")
        avg_distances = results[group_name]["average"]
        std_distances = results[group_name]["std"]

        for model_file in comparison_data.keys():
            txt_file.write(f"Model: {model_file}\n")
            txt_file.write(f"  Avg Dist: {avg_distances[model_file]}\n")
            txt_file.write(f"  Std Dist: {std_distances[model_file]}\n\n")

    txt_file.write("Done.\n")

print("Distances by group saved to 'model_distances.txt'.")

