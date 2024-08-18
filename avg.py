import json
import math
import os

# Function to load JSON data
def load_json(file_path):
    with open(file_path, 'r') as file:
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
                if metric in metrics_min_max:  # Check necessary due to skipping empty dictionaries earlier
                    min_val = metrics_min_max[metric]['min']
                    max_val = metrics_min_max[metric]['max']
                    if max_val != min_val:
                        normalized_value = (value - min_val) / (max_val - min_val)
                        entry['metrics'][metric] = normalized_value
                    else:
                        entry['metrics'][metric] = 0.0  # Avoid division by zero

# Function to calculate Euclidean distance between two dictionaries of metrics
def euclidean_distance(metrics1, metrics2, include_metrics=None):
    if include_metrics is not None:
        # Filter to include only specified metrics if include_metrics is provided
        common_keys = set(metrics1.keys()).intersection(metrics2.keys()).intersection(include_metrics)
    else:
        # Use all common keys if no specific metrics are provided
        common_keys = set(metrics1.keys()).intersection(metrics2.keys())

    if not common_keys:
        return float('inf')  # Return infinite if no common metrics to compare

    sum_squares = sum((metrics1[key] - metrics2[key]) ** 2 for key in common_keys)
    return math.sqrt(sum_squares)

# List of JSON filenames provided by the user
json_filenames = ["nilc_reference.json", "nilc_opt-ft.json", "nilc_opt-gt5.json", "nilc_opt-gt7.json",
                  "nilc_opt-lora.json", "nilc_ptt5_ft.json", "nilc_ptt5_gt5.json", "nilc_ptt5_gt7.json",
                  "nilc_ptt5_lora.json"]  # Replace ... with actual filenames

# Load all JSON data
all_data = {f: load_json(f) for f in json_filenames}

# Find min and max values for each metric
metrics_min_max = find_min_max_metrics(all_data)

#print(metrics_min_max)

# Normalize the data
normalize_data(all_data, metrics_min_max)

# The first JSON file is the reference
reference_data = all_data[json_filenames[0]]
comparison_data = {f: data for f, data in all_data.items() if f != json_filenames[0]}


simplicidade = ["dialog_pronoun_ratio", "easy_conjunctions_ratio", "hard_conjunctions_ratio", "long_sentence_ratio",
                "medium_long_sentence_ratio", "medium_short_sentence_ratio", "short_sentence_ratio", "simple_word_ratio"]

coesao_referencial = ["adjacent_refs", "anaphoric_refs", "adj_arg_ovl", "adj_cw_ovl", "adj_stem_ovl", "arg_ovl",
                      "stem_ovl", "coreference_pronoun_ratio", "demonstrative_pronoun_ratio"]

coesao_semantica = ["lsa_adj_mean", "lsa_adj_std", "lsa_all_mean", "lsa_all_std", "lsa_givenness_mean",
                    "lsa_givenness_std", "lsa_paragraph_mean", "lsa_paragraph_std", "lsa_span_mean",
                    "lsa_span_std", "cross_entropy"]

complexidade_sintatica = ["words_before_main_verb", "adjunct_per_clause", "adverbs_before_main_verb_ratio", "apposition_per_clause",
                          "clauses_per_sentence", "coordinate_conjunctions_per_clauses", "dep_distance", "frazier",
                          "infinite_subordinate_clauses", "non_svo_ratio", "passive_ratio", "postponed_subject_ratio",
                          "ratio_coordinate_conjunctions", "ratio_subordinate_conjunctions", "relative_clauses", "sentences_with_five_clauses",
                          "sentences_with_four_clauses", "sentences_with_one_clause", "sentences_with_seven_more_clauses",
                          "sentences_with_six_clauses", "sentences_with_three_clauses", "sentences_with_two_clauses",
                          "sentences_with_zero_clause", "std_noun_phrase", "subordinate_clauses", "temporal_adjunct_ratio",
                          "yngve"]

leiturabilidade = ["brunet", "dalechall_adapted", "flesch", "gunning_fox", "honore"]

morfosintaxe = ["adjective_ratio", "adverbs", "content_words", "function_words", "noun_ratio", "pronoun_ratio",
                "verbs", "personal_pronouns", "adjectives_max", "adjectives_min", "adjectives_standard_deviation",
                "adverbs_diversity_ratio", "adverbs_max", "adverbs_min", "adverbs_standard_deviation", "indefinite_pronoun_ratio",
                "indicative_condition_ratio", "indicative_future_ratio", "infinitive_verbs", "inflected_verbs", "non-inflected_verbs",
                "nouns_max", "nouns_min", "nouns_standard_deviation", "oblique_pronouns_ratio", "prepositions_per_clause",
                "prepositions_per_sentence", "pronouns_max", "pronouns_min", "pronouns_standard_deviation", "punctuation_ratio",
                "ratio_function_to_content_words", "relative_pronouns_ratio", "second_person_possessive_pronouns",
                "second_person_pronouns", "third_person_possessive_pronouns", "third_person_pronouns", "verbs_max",
                "verbs_min", "verbs_standard_deviation", "first_person_possessive_pronouns", "first_person_pronouns"]



info_semantica = ["adjectives_ambiguity", "adverbs_ambiguity", "nouns_ambiguity", "verbs_ambiguity", "hypernyms_verbs",
                  "abstract_nouns_ratio", "content_words_ambiguity", "named_entity_ratio_sentence", "named_entity_ratio_text",
                  "negative_words", "positive_words"]

print(len(info_semantica))

# Compute distances
distances = {}
for key in reference_data:
    if not reference_data[key]['metrics']:  # Skip if reference has empty metrics
        continue
    distances[key] = {}
    for f, data in comparison_data.items():
        if key in data and data[key]['metrics']:  # Check both sides have metrics
            distances[key][f] = euclidean_distance(reference_data[key]['metrics'], data[key]['metrics'], morfosintaxe)

# Compute average distances for each model
average_distances = {}
for f in comparison_data.keys():
    total_distance = 0
    count = 0
    for key, dists in distances.items():
        if f in dists and dists[f] != float('inf'):
            total_distance += dists[f]
            count += 1
    if count > 0:
        average_distances[f] = total_distance / count
    else:
        average_distances[f] = float('inf')  # Handle case where no distances were valid

# Output distances and average distances
# print("Detailed Key-by-Key Distances:")
# print(json.dumps(distances, indent=4))
# print("Average Distances by Model:")
# print(json.dumps(average_distances, indent=4))
