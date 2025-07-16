import sys
import os

# Import necessary helper functions from the recall module
# This creates a dependency: evaluation_dimension_coverage_all_flags_before_answering.py depends on evaluation_dimension_recall.py
sys.path.append(os.path.dirname(os.path.abspath(__file__))) # Add current directory to path for imports
from evaluation_dimension_recall import _extract_constrained_flags, _normalize_text

# --- Core Evaluation Function: Coverage of All Flags Before Answering ---
def evaluate_coverage_all_flags_before_answering(response_text, expected_flags):
    """
    Measures Coverage of All Flags Before Answering: Did the model list all expected assumptions
    before providing any explanation?
    
    Args:
        response_text (str): The full constrained LLM response text.
        expected_flags (list): A list of normalized strings of ground truth assumptions.
        
    Returns:
        dict: A dictionary containing the coverage status, success status, and error message.
    """
    try:
        # Extract detected flags using the helper function
        detected_flags, _ = _extract_constrained_flags(response_text)
        
        expected_set = set(expected_flags)
        detected_set = set(detected_flags)
        
        # Check if all expected flags are present in the detected flags
        # This means expected_set is a subset of detected_set
        all_covered = expected_set.issubset(detected_set)
        
        return {
            'all_flags_covered_before_answer': all_covered,
            'success': True,
            'error_message': None
        }
    except Exception as e:
        return {
            'all_flags_covered_before_answer': False, # Default to False on error
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_coverage_all_flags_before_answering.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Example responses (assuming _extract_constrained_flags works)
    sample_response_1 = """Assumptions:
1. The sky is always blue. (Incorrect, can be grey/red at times.)
2. Birds can fly.
Answer: This is the answer."""

    sample_response_2 = """Assumptions:
1. All birds can fly. (Incorrect, penguins cannot fly.)

Answer: Not all birds can fly."""

    sample_response_3 = """Assumptions:
1. Only one flag.
2. Another flag.
Answer: ..."""

    sample_response_4 = """Assumptions:

Answer: ..."""

    # Test Case 1: All expected flags covered
    expected_1 = [_normalize_text("The sky is always blue."), _normalize_text("Birds can fly.")]
    result_1 = evaluate_coverage_all_flags_before_answering(sample_response_1, expected_1)
    print(f"\nTest Case 1 (All flags covered): {result_1}", file=sys.stderr) # Expected: True

    # Test Case 2: Not all expected flags covered (missing one)
    expected_2 = [_normalize_text("All birds can fly."), _normalize_text("Penguins are fish.")] # Expected two
    result_2 = evaluate_coverage_all_flags_before_answering(sample_response_2, expected_2)
    print(f"Test Case 2 (Not all flags covered): {result_2}", file=sys.stderr) # Expected: False (only "All birds can fly." is detected)

    # Test Case 3: More flags detected than expected (but all expected are covered)
    expected_3 = [_normalize_text("Only one flag.")]
    result_3 = evaluate_coverage_all_flags_before_answering(sample_response_3, expected_3)
    print(f"Test Case 3 (More detected than expected, but covered): {result_3}", file=sys.stderr) # Expected: True

    # Test Case 4: No expected flags
    expected_4 = []
    result_4 = evaluate_coverage_all_flags_before_answering(sample_response_4, expected_4)
    print(f"Test Case 4 (No expected flags): {result_4}", file=sys.stderr) # Expected: True (trivially covered)

    # Test Case 5: Expected flags, but no flags detected
    expected_5 = [_normalize_text("Expected but not found.")]
    response_5 = """Assumptions:

Answer: ..."""
    result_5 = evaluate_coverage_all_flags_before_answering(response_5, expected_5)
    print(f"Test Case 5 (Expected but none detected): {result_5}", file=sys.stderr) # Expected: False
