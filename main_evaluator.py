import os
import json
from datetime import datetime
import subprocess
import csv
import sys
from collections import defaultdict

# Import all individual dimension measurement functions using YOUR EXACT FILENAMES
# IMPORTANT: Ensure these files are in the same directory as this script.
from count_test import measure_length_and_tokens
from stanza_syntactic_comp_test import measure_stanza_semantic_complexity
from spacy_voice_detection import measure_spacy_voice_detection
from spacy_logical_mark_test import measure_logical_markers
from spacy_negation_hedge_test import measure_negation_hedging
from domain_sp_test import measure_domain_specific_terms
from abstractness_test import measure_concreteness_score
from spacy_pronoun_test import measure_spacy_pronoun_detection
from nested_spacy_depen_test import measure_spacy_compound_assumptions
from nested_stanza_const_test import measure_stanza_compound_assumptions
from spacy_leven_dist_test import measure_paraphrase_distance


# --- Global File Paths (Centralized for all dimensions) ---
BASE_DIR = r"C:\Users\ja\Documents\LLM_Eval"
DOMAIN_TERMS_FILEPATH = os.path.join(BASE_DIR, "domain_sp_words.txt")
CONCRETENESS_CSV_PATH = os.path.join(BASE_DIR, "concreteness_scores_original.csv")

# --- Coreferee Specific Paths ---
COREF_ENV_PYTHON_PATH = os.path.join(BASE_DIR, "coref_env", "Scripts", "python.exe")
COREF_REPORTER_SCRIPT_PATH = os.path.join(BASE_DIR, "coreferee_reporter.py")

# --- JSONL Report Path (Output) ---
JSONL_REPORT_FILEPATH = os.path.join(BASE_DIR, "query_analysis_report.jsonl")


# --- Helper function to run Coreferee analysis in its separate environment ---
def _run_coreferee_analysis_subprocess(text_to_analyze):
    results = {
        'total_coref_chains': 0,
        'pronouns_in_chains_count': 0,
        'coreference_chains_info': [],
        'success': False,
        'error_message': "Failed to run Coreferee analysis."
    }
    
    try:
        command = [
            COREF_ENV_PYTHON_PATH,
            COREF_REPORTER_SCRIPT_PATH,
            text_to_analyze
        ]
        
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )
        
        coreferee_output_json = process.stdout.strip()
        
        if coreferee_output_json:
            coreferee_data = json.loads(coreferee_output_json)
            results.update(coreferee_data)
        else:
            results['error_message'] = "Coreferee script returned empty output."

    except FileNotFoundError:
        results['error_message'] = f"Python executable not found at '{COREF_ENV_PYTHON_PATH}' or script not found at '{COREF_REPORTER_SCRIPT_PATH}'. Check paths."
    except subprocess.CalledProcessError as e:
        results['error_message'] = f"Coreferee script failed with exit code {e.returncode}. Stderr: {e.stderr.strip()}"
    except json.JSONDecodeError:
        results['error_message'] = f"Coreferee script returned invalid JSON. Output: {coreferee_output_json}"
    except Exception as e:
        results['error_message'] = f"An unexpected error occurred during Coreferee subprocess call: {e}"

    return results


# --- Helper function to write results to JSONL ---
def _write_to_jsonl(data_dict, filepath):
    """
    Appends a single dictionary (converted to a JSON string) as a new line to a .jsonl file.
    """
    try:
        with open(filepath, 'a', encoding='utf-8') as f: # Ensure 'a' (append) mode is used
            json.dump(data_dict, f)
            f.write('\n') # Write a newline character to separate JSON objects
    except Exception as e:
        print(f"Error writing to JSONL file {filepath}: {e}", file=sys.stderr)


# --- Function to analyze a single text for its core dimensions (excluding paraphrase distance) ---
def _analyze_text_core_dimensions(text_to_analyze):
    """
    Runs all core linguistic dimension tests on a single text.
    Does NOT include paraphrase distance calculation.
    """
    dimensions_results = {}

    # 1. Length and Tokens
    dimensions_results["length_and_tokens"] = measure_length_and_tokens(text_to_analyze)

    # 2. Semantic Complexity - Stanza (Parse Tree Depth & Subordinate Clauses)
    dimensions_results["semantic_complexity_stanza"] = measure_stanza_semantic_complexity(text_to_analyze)

    # 3. Semantic Complexity - spaCy (Voice Detection)
    dimensions_results["semantic_complexity_spacy_voice"] = measure_spacy_voice_detection(text_to_analyze)

    # 4. Logical Markers
    dimensions_results["logical_markers"] = measure_logical_markers(text_to_analyze)

    # 5. Negation and Hedging
    dimensions_results["negation_and_hedging"] = measure_negation_hedging(text_to_analyze)

    # 6. Domain-Specific Terms
    dimensions_results["domain_specific_terms"] = measure_domain_specific_terms(text_to_analyze, DOMAIN_TERMS_FILEPATH)

    # 7. Abstractness vs. Concreteness
    dimensions_results["abstractness_concreteness"] = measure_concreteness_score(text_to_analyze, CONCRETENESS_CSV_PATH)

    # 8. Ambiguity - spaCy Pronoun Detection
    dimensions_results["ambiguity_spacy_pronoun"] = measure_spacy_pronoun_detection(text_to_analyze)

    # 9. Compound Assumptions - spaCy (Dependency)
    dimensions_results["compound_assumptions_spacy"] = measure_spacy_compound_assumptions(text_to_analyze)

    # 10. Compound Assumptions - Stanza (Constituency)
    dimensions_results["compound_assumptions_stanza"] = measure_stanza_compound_assumptions(text_to_analyze)

    # 11. Coreferee Analysis (via subprocess)
    dimensions_results["ambiguity_coreferee"] = _run_coreferee_analysis_subprocess(text_to_analyze)

    return dimensions_results


# --- Main function to process the grouped queries and generate nested JSONL ---
def process_queries_and_paraphrases(grouped_input_data):
    """
    Processes grouped query and paraphrase data, performs analysis,
    and writes results to a JSONL file with nested paraphrase data.

    Args:
        grouped_input_data (dict): A dictionary where keys are unique original query texts,
                                   and values are lists of dictionaries (rows from input CSV)
                                   containing the query and its associated paraphrases.
    """
    total_unique_queries_processed = 0
    for query_text, related_entries in grouped_input_data.items():
        total_unique_queries_processed += 1
        print(f"\n--- Processing Unique Query {total_unique_queries_processed}: '{query_text[:70]}...' ---")

        # Get the full analysis for the original query text
        original_query_dimensions = _analyze_text_core_dimensions(query_text)
        
        paraphrases_data_list = []
        # Iterate through related_entries to find actual paraphrases
        for entry_row in related_entries:
            paraphrase_text = entry_row.get('paraphrase_text', '').strip()
            
            # Only process if paraphrase_text is present and not the same as the original query text
            # This avoids processing the original query as its own paraphrase
            if paraphrase_text and paraphrase_text != query_text:
                print(f"  - Analyzing Paraphrase: '{paraphrase_text[:70]}...'")
                
                # Analyze paraphrase for its own dimensions (e.g., length, voice, etc.)
                paraphrase_own_dimensions = _analyze_text_core_dimensions(paraphrase_text)

                # Calculate paraphrase distance to the original query
                word_level_distance_results = measure_paraphrase_distance(query_text, paraphrase_text, level="word")
                char_level_distance_results = measure_paraphrase_distance(query_text, paraphrase_text, level="char")

                paraphrases_data_list.append({
                    "paraphrase_text": paraphrase_text,
                    "paraphrase_dimensions": paraphrase_own_dimensions,
                    "paraphrase_distance_to_original": {
                        "word_level": word_level_distance_results,
                        "char_level": char_level_distance_results
                    }
                })
        
        # Construct the final nested report for this unique query
        final_report_for_query = {
            "query_text": query_text,
            "analysis_timestamp": datetime.now().isoformat(),
            "original_query_dimensions": original_query_dimensions,
            "paraphrases": paraphrases_data_list # This list will be empty if no paraphrases were found/provided
        }
        
        # Write this single, nested JSON object to the .jsonl file
        _write_to_jsonl(final_report_for_query, JSONL_REPORT_FILEPATH)
        print(f"  Report for '{query_text[:70]}...' appended to {JSONL_REPORT_FILEPATH}")

    print(f"\n--- Batch processing completed for {total_unique_queries_processed} unique queries. ---")


if __name__ == "__main__":
    print("--- Running Master Script 1: Main Dimensions Reporter (Grouped JSONL Output - Final Fix) ---")
    print("Ensures one JSON object per unique original query, with paraphrases nested.")
    print("="*80)
    print("Ensure all individual dimension scripts are in the same directory.")
    print("Ensure 'coreferee_reporter.py' is also in this directory.")
    print("Ensure you are running this in your MAIN virtual environment.")
    print(f"Results will be written to: {JSONL_REPORT_FILEPATH}")
    print("="*80)

    input_csv_path = input("\nEnter the full path to your input CSV file (e.g., C:\\Users\\ja\\Documents\\LLM_Eval\\my_queries.csv): ").strip()

    if not os.path.exists(input_csv_path):
        print(f"Error: Input CSV file not found at '{input_csv_path}'. Please check the path and try again.", file=sys.stderr)
        sys.exit(1)

    # Read and group all queries from the input CSV
    grouped_queries_data = defaultdict(list)
    
    try:
        with open(input_csv_path, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            
            if 'query_text' not in reader.fieldnames:
                print(f"Error: Input CSV must contain a 'query_text' column. Found: {reader.fieldnames}", file=sys.stderr)
                sys.exit(1)
            
            # Add paraphrase_text to fieldnames if it's missing, so we can still access it
            if 'paraphrase_text' not in reader.fieldnames:
                reader.fieldnames.append('paraphrase_text')
                print(f"Warning: 'paraphrase_text' column not found in input CSV header. Paraphrase distance will be skipped for rows without this column explicitly defined or if cells are empty.", file=sys.stderr)

            for row_num, row in enumerate(reader, start=1):
                query_text = row.get('query_text', '').strip()
                
                if not query_text:
                    print(f"Skipping empty 'query_text' in row {row_num} of input CSV.", file=sys.stderr)
                    continue
                
                grouped_queries_data[query_text].append(row) # Group by query_text

        if not grouped_queries_data:
            print("No valid queries found in the input CSV file after grouping. Exiting.", file=sys.stderr)
            sys.exit(0)

    except Exception as e:
        print(f"An error occurred while reading or grouping the input CSV: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure the JSONL file is empty before starting a new run
    # This prevents old data from accumulating if the input CSV changes
    if os.path.exists(JSONL_REPORT_FILEPATH):
        try:
            os.remove(JSONL_REPORT_FILEPATH)
            print(f"Cleaned up existing '{JSONL_REPORT_FILEPATH}' before new run.", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not remove existing '{JSONL_REPORT_FILEPATH}': {e}", file=sys.stderr)

    # Process the grouped data
    process_queries_and_paraphrases(grouped_queries_data)