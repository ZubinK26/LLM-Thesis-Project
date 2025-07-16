import sys

# --- Core Evaluation Function: Assumption Precision ---
def evaluate_assumption_precision(expected_flags, detected_flags):
    """
    Measures Assumption Precision: Proportion of flagged items that truly were false assumptions.
    
    Args:
        expected_flags (list): A list of normalized strings of ground truth assumptions.
        detected_flags (list): A list of normalized strings of assumptions detected from the LLM's response.
        
    Returns:
        dict: A dictionary containing the precision score, classification, success status, and error message.
    """
    try:
        if not detected_flags:
            # If the model didn't detect any flags, precision is perfectly met (trivially true)
            return {
                'precision_score': 1.0,
                'classification': 'N/A (No flags detected)',
                'success': True,
                'error_message': None
            }
        
        # Convert to sets for efficient intersection
        expected_set = set(expected_flags)
        detected_set = set(detected_flags)

        correct_flags = detected_set.intersection(expected_set)
        precision = len(correct_flags) / len(detected_set)
        
        if precision >= 0.8:
            classification = "High"
        elif precision >= 0.5:
            classification = "Medium"
        else:
            classification = "Low"
            
        return {
            'precision_score': precision,
            'classification': classification,
            'success': True,
            'error_message': None
        }
    except Exception as e:
        return {
            'precision_score': 0.0, # Default to 0 on error
            'classification': 'Error',
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_precision.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Test Case 1: Perfect Precision (all detected are correct)
    expected_1 = ['apple', 'banana', 'cherry']
    detected_1 = ['apple', 'banana'] # Only detected correct ones
    result_1 = evaluate_assumption_precision(expected_1, detected_1)
    print(f"\nTest Case 1 (Perfect Precision): {result_1}", file=sys.stderr) # Expected: High (1.0)

    # Test Case 2: Some False Positives
    expected_2 = ['apple', 'banana', 'cherry']
    detected_2 = ['apple', 'grape', 'banana'] # 'grape' is a false positive
    result_2 = evaluate_assumption_precision(expected_2, detected_2)
    print(f"Test Case 2 (Some False Positives): {result_2}", file=sys.stderr) # Expected: Medium (2/3 = 0.66)

    # Test Case 3: All False Positives
    expected_3 = ['apple', 'banana', 'cherry']
    detected_3 = ['grape', 'orange'] # All false positives
    result_3 = evaluate_assumption_precision(expected_3, detected_3)
    print(f"Test Case 3 (All False Positives): {result_3}", file=sys.stderr) # Expected: Low (0.0)

    # Test Case 4: No Detected Flags
    expected_4 = ['apple', 'banana']
    detected_4 = []
    result_4 = evaluate_assumption_precision(expected_4, detected_4)
    print(f"Test Case 4 (No Detected Flags): {result_4}", file=sys.stderr) # Expected: N/A (1.0)

    # Test Case 5: No Expected Flags, No Detected Flags
    expected_5 = []
    detected_5 = []
    result_5 = evaluate_assumption_precision(expected_5, detected_5)
    print(f"Test Case 5 (No Expected, No Detected): {result_5}", file=sys.stderr) # Expected: N/A (1.0)

    # Test Case 6: No Expected Flags, But Detected Flags (Hallucination)
    expected_6 = []
    detected_6 = ['hallucinated_flag']
    result_6 = evaluate_assumption_precision(expected_6, detected_6)
    print(f"Test Case 6 (No Expected, Detected Hallucination): {result_6}", file=sys.stderr) # Expected: Low (0.0)
