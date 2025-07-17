import os
import json
import csv
import sys
from datetime import datetime
import spacy # For passing to conciseness module

# --- Adjust Python path to import modules from evaluation_modules directory ---
# This ensures that our master script can find and import the individual dimension modules.
# It adds the directory where this script resides (LLM_Response_Eval) to the Python path,
# allowing relative imports like 'evaluation_modules.evaluation_dimension_recall'.
# Note: This path adjustment might not be strictly necessary if run_llm_evaluation.py is
# always run from its directory and evaluation_modules is a direct subdirectory.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# --- Import all necessary evaluation dimension functions and helpers ---
# We import specific functions, not the whole module, for clarity.
# _normalize_text and _extract_constrained_flags are central helpers used by multiple dimensions.
from evaluation_modules.evaluation_dimension_recall import (
    _normalize_text,
    _extract_constrained_flags,
    evaluate_assumption_recall
)
from evaluation_modules.evaluation_dimension_precision import evaluate_assumption_precision
from evaluation_modules.evaluation_dimension_total_flags_count import evaluate_total_flags_count
from evaluation_modules.evaluation_dimension_format_compliance import evaluate_format_compliance
from evaluation_modules.evaluation_dimension_justification_conciseness import evaluate_justification_conciseness
from evaluation_modules.evaluation_dimension_hallucinated_flag_rate import evaluate_hallucinated_flag_rate
from evaluation_modules.evaluation_dimension_coverage_all_flags_before_answering import evaluate_coverage_all_flags_before_answering
from evaluation_modules.evaluation_dimension_hedging_count import evaluate_hedging_count # NEW IMPORT


# --- Global File Paths ---
# Assuming BASE_DIR is the root of your entire project (C:\Users\ja\Documents\LLM_Eval)
BASE_DIR = r"C:\Users\ja\Documents\LLM_Eval"
LLM_RESPONSE_EVAL_DIR = os.path.join(BASE_DIR, "LLM_Response_Eval")

GROUND_TRUTH_ASSUMPTIONS_CSV = os.path.join(LLM_RESPONSE_EVAL_DIR, "ground_truth_assumptions.csv")
LLM_RESPONSES_CSV = os.path.join(LLM_RESPONSE_EVAL_DIR, "llm_responses.csv")
LLM_EVAL_REPORT_JSONL = os.path.join(LLM_RESPONSE_EVAL_DIR, "llm_eval_report.jsonl")

# --- Load spaCy model once for the entire evaluation run ---
# This is loaded here in the master script and passed to modules that need it,
# avoiding multiple loads and ensuring consistency.
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("SpaCy 'en_core_web_md' model not found. This is required for some metrics.", file=sys.stderr)
    print("Please run 'python -m spacy download en_core_web_md' in your terminal.", file=sys.stderr)
    sys.exit(1)


# --- Helper Function to write results to JSONL ---
def _write_to_jsonl(data_dict, filepath):
    """
    Appends a single dictionary (converted to a JSON string) as a new line to a .jsonl file.
    """
    try:
        with open(filepath, 'a', encoding='utf-8') as f:
            json.dump(data_dict, f)
            f.write('\n')
    except Exception as e:
        print(f"Error writing to JSONL file {filepath}: {e}", file=sys.stderr)


# --- Helper Function to Load Ground Truth Assumptions ---
def _load_ground_truth_assumptions(filepath):
    """
    Loads ground truth assumptions from a CSV into a dictionary.
    Expected CSV format: QueryID,ExpectedAssumptions (JSON string of list)
    """
    ground_truth = {}
    try:
        with open(filepath, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                query_id = row.get('QueryID')
                expected_assumptions_str = row.get('ExpectedAssumptions', '[]')
                if query_id:
                    try:
                        # Parse the JSON string into a Python list of strings
                        expected_list = json.loads(expected_assumptions_str)
                        # Normalize each expected assumption using the helper from recall module
                        ground_truth[query_id] = [_normalize_text(a) for a in expected_list]
                    except json.JSONDecodeError as e:
                        print(f"Warning: Could not parse ExpectedAssumptions for QueryID '{query_id}'. Skipping. Raw: '{expected_assumptions_str}'. Error: {e}", file=sys.stderr)
                        ground_truth[query_id] = [] # Assign empty list on parse error
    except FileNotFoundError:
        print(f"Error: Ground truth file not found at '{filepath}'. Please check the path.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred loading ground truth assumptions: {e}", file=sys.stderr)
        sys.exit(1)
    return ground_truth


# --- Main Evaluation Logic ---
def run_llm_evaluation():
    """
    Orchestrates the LLM response evaluation process.
    """
    print(f"Loading ground truth assumptions from: {GROUND_TRUTH_ASSUMPTIONS_CSV}")
    ground_truth_map = _load_ground_truth_assumptions(GROUND_TRUTH_ASSUMPTIONS_CSV)
    print(f"Loaded {len(ground_truth_map)} ground truth entries.")

    print(f"Loading LLM responses from: {LLM_RESPONSES_CSV}")
    llm_responses = []
    try:
        with open(LLM_RESPONSES_CSV, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            # Ensure required columns exist as per the format defined
            required_cols = ['QueryID', 'QueryText', 'ConstrainedLLMResponse', 'UnconstrainedLLMResponse', 'ModelName', 'RunID']
            if not all(col in reader.fieldnames for col in required_cols):
                print(f"Error: Missing one or more required columns in '{LLM_RESPONSES_CSV}'. "
                      f"Required: {required_cols}. Found: {reader.fieldnames}", file=sys.stderr)
                sys.exit(1)
            for row in reader:
                llm_responses.append(row)
        if not llm_responses:
            print(f"No LLM responses found in '{LLM_RESPONSES_CSV}'. Exiting.", file=sys.stderr)
            return
    except FileNotFoundError:
        print(f"Error: LLM responses file not found at '{LLM_RESPONSES_CSV}'. Please check the path.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred loading LLM responses: {e}", file=sys.stderr)
        sys.exit(1)

    # Ensure the output JSONL file is empty before starting a new run
    if os.path.exists(LLM_EVAL_REPORT_JSONL):
        try:
            os.remove(LLM_EVAL_REPORT_JSONL)
            print(f"Cleaned up existing '{LLM_EVAL_REPORT_JSONL}' before new run.", file=sys.stderr)
        except Exception as e:
            print(f"Warning: Could not remove existing '{LLM_EVAL_REPORT_JSONL}': {e}", file=sys.stderr)

    total_responses_evaluated = 0
    for response_entry in llm_responses:
        total_responses_evaluated += 1
        query_id = response_entry.get('QueryID')
        query_text = response_entry.get('QueryText')
        constrained_response = response_entry.get('ConstrainedLLMResponse', '')
        unconstrained_response = response_entry.get('UnconstrainedLLMResponse', '')
        model_name = response_entry.get('ModelName', 'N/A')
        run_id = response_entry.get('RunID', 'N/A')

        print(f"\n--- Evaluating Response {total_responses_evaluated} (QueryID: {query_id}, Model: {model_name}) ---")
        
        expected_flags_for_query = ground_truth_map.get(query_id, [])
        if not expected_flags_for_query:
            print(f"  Warning: No expected assumptions found for QueryID '{query_id}'.")

        # --- IMPORTANT: Extract detected flags and justifications ONCE ---
        # These results are then passed to multiple evaluation functions.
        detected_flags_normalized, justifications_raw = _extract_constrained_flags(constrained_response)
        
        # --- Run all evaluation dimensions ---
        eval_results = {
            "query_id": query_id,
            "query_text": query_text,
            "model_name": model_name,
            "run_id": run_id,
            "evaluation_timestamp": datetime.now().isoformat(),
            "constrained_response_text": constrained_response,
            "unconstrained_response_text": unconstrained_response, # Included for completeness
            "expected_assumptions_normalized": expected_flags_for_query,
            "detected_flags_constrained_normalized": detected_flags_normalized,
            "detected_justifications_constrained_raw": justifications_raw,
            "constrained_evaluation_results": {
                "assumption_recall": evaluate_assumption_recall(expected_flags_for_query, detected_flags_normalized),
                "assumption_precision": evaluate_assumption_precision(expected_flags_for_query, detected_flags_normalized),
                "total_flags_count": evaluate_total_flags_count(detected_flags_normalized),
                "format_compliance": evaluate_format_compliance(constrained_response),
                "justification_conciseness": evaluate_justification_conciseness(justifications_raw, nlp), # Pass nlp model
                "hallucinated_flag_rate": evaluate_hallucinated_flag_rate(expected_flags_for_query, detected_flags_normalized),
                "coverage_all_flags_before_answering": evaluate_coverage_all_flags_before_answering(constrained_response, expected_flags_for_query),
                
                # Placeholder Dimensions (as discussed, these require more complex setup)
                "pause_proceed_compliance": {'compliant': 'N/A', 'details': 'Requires interactive session logging.', 'success': False, 'error_message': 'Not Implemented'},
                "justification_correctness": {'correctness_ratio': 'N/A', 'classification': 'N/A', 'details': 'Requires human review or LLM probe.', 'success': False, 'error_message': 'Not Implemented'},
                "explanation_readiness": {'ready': 'N/A', 'details': 'Requires interactive session logging.', 'success': False, 'error_message': 'Not Implemented'}
            },
            # NEW UNCONSTRAINED EVALUATION RESULTS SECTION
            "unconstrained_evaluation_results": {
                "hedging_count": evaluate_hedging_count(unconstrained_response) # NEW METRIC
            }
        }
        
        _write_to_jsonl(eval_results, LLM_EVAL_REPORT_JSONL)
        print(f"  Evaluation for QueryID '{query_id}' (Model: {model_name}) appended to {LLM_EVAL_REPORT_JSONL}")

    print(f"\n--- LLM Response Evaluation completed for {total_responses_evaluated} responses. ---")


if __name__ == "__main__":
    print("--- Running LLM Response Evaluation Framework: Master Evaluator ---")
    print("This script orchestrates the evaluation of LLM responses based on predefined dimensions.")
    print("="*80)
    print(f"Ground Truth File: {GROUND_TRUTH_ASSUMPTIONS_CSV}")
    print(f"LLM Responses Input File: {LLM_RESPONSES_CSV}")
    print(f"Output Report File: {LLM_EVAL_REPORT_JSONL}")
    print("="*80)

    run_llm_evaluation()