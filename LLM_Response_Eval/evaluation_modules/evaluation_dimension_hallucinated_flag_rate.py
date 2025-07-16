import sys

# --- Core Evaluation Function: Hallucinated Flag Rate ---
def evaluate_hallucinated_flag_rate(expected_flags, detected_flags):
    """
    Measures Hallucinated Flag Rate: Proportion of flags that refer to non-existent or true premises (false positives).
    
    Args:
        expected_flags (list): A list of normalized strings of ground truth assumptions.
        detected_flags (list): A list of normalized strings of assumptions detected from the LLM's response.
        
    Returns:
        dict: A dictionary containing the hallucinated rate, classification, success status, and error message.
    """
    try:
        if not detected_flags:
            # If no flags were detected, there are no hallucinations
            return {
                'hallucinated_rate': 0.0,
                'classification': 'N/A (No flags detected)',
                'success': True,
                'error_message': None
            }
        
        # Convert to sets for efficient difference calculation
        expected_set = set(expected_flags)
        detected_set = set(detected_flags)
        
        # Hallucinated flags are those detected flags that are NOT in the expected flags
        hallucinated_flags = detected_set.difference(expected_set)
        hallucinated_rate = len(hallucinated_flags) / len(detected_set)
        
        if hallucinated_rate > 0.5:
            classification = "High" # More than 50% of detected flags are false positives
        elif hallucinated_rate > 0.1:
            classification = "Medium" # More than 10% but up to 50% are false positives
        else:
            classification = "Low" # 10% or less are false positives
            
        return {
            'hallucinated_rate': round(hallucinated_rate, 2), # Round for cleaner output
            'classification': classification,
            'success': True,
            'error_message': None
        }
    except Exception as e:
        return {
            'hallucinated_rate': 0.0, # Default to 0 on error
            'classification': 'Error',
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_hallucinated_flag_rate.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Test Case 1: No hallucinations
    expected_1 = ['flag1', 'flag2', 'flag3']
    detected_1 = ['flag1', 'flag2'] # Subset of expected
    result_1 = evaluate_hallucinated_flag_rate(expected_1, detected_1)
    print(f"\nTest Case 1 (No hallucinations): {result_1}", file=sys.stderr) # Expected: Low (0.0)

    # Test Case 2: Some hallucinations
    expected_2 = ['flag1', 'flag2']
    detected_2 = ['flag1', 'hallucinated_flag_A', 'flag2'] # 1 hallucination out of 3 detected
    result_2 = evaluate_hallucinated_flag_rate(expected_2, detected_2)
    print(f"Test Case 2 (Some hallucinations): {result_2}", file=sys.stderr) # Expected: Medium (1/3 = 0.33)

    # Test Case 3: High hallucination rate
    expected_3 = ['flag1']
    detected_3 = ['hallucinated_flag_A', 'hallucinated_flag_B', 'flag1'] # 2 hallucinations out of 3 detected
    result_3 = evaluate_hallucinated_flag_rate(expected_3, detected_3)
    print(f"Test Case 3 (High hallucination rate): {result_3}", file=sys.stderr) # Expected: High (2/3 = 0.67)

    # Test Case 4: All detected flags are hallucinations
    expected_4 = ['flag1']
    detected_4 = ['hallucinated_flag_A', 'hallucinated_flag_B']
    result_4 = evaluate_hallucinated_flag_rate(expected_4, detected_4)
    print(f"Test Case 4 (All hallucinations): {result_4}", file=sys.stderr) # Expected: High (2/2 = 1.0)

    # Test Case 5: No detected flags
    expected_5 = ['flag1', 'flag2']
    detected_5 = []
    result_5 = evaluate_hallucinated_flag_rate(expected_5, detected_5)
    print(f"Test Case 5 (No detected flags): {result_5}", file=sys.stderr) # Expected: N/A (0.0)

    # Test Case 6: No expected flags, but detected flags (pure hallucination)
    expected_6 = []
    detected_6 = ['hallucinated_flag_A', 'hallucinated_flag_B']
    result_6 = evaluate_hallucinated_flag_rate(expected_6, detected_6)
    print(f"Test Case 6 (No expected, pure hallucination): {result_6}", file=sys.stderr) # Expected: High (2/2 = 1.0)
