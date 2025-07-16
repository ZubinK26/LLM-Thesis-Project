import sys

# --- Core Evaluation Function: Total Flags Count ---
def evaluate_total_flags_count(detected_flags):
    """
    Measures Total Flags Count: Absolute number of assumptions flagged.
    
    Args:
        detected_flags (list): A list of normalized strings of assumptions detected from the LLM's response.
        
    Returns:
        dict: A dictionary containing the total flags count, success status, and error message.
    """
    try:
        count = len(detected_flags)
        return {
            'total_flags_count': count,
            'success': True,
            'error_message': None
        }
    except Exception as e:
        return {
            'total_flags_count': 0, # Default to 0 on error
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_total_flags_count.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Test Case 1: Multiple flags
    detected_1 = ['flag1', 'flag2', 'flag3']
    result_1 = evaluate_total_flags_count(detected_1)
    print(f"\nTest Case 1 (Multiple flags): {result_1}", file=sys.stderr) # Expected: {'total_flags_count': 3, ...}

    # Test Case 2: No flags
    detected_2 = []
    result_2 = evaluate_total_flags_count(detected_2)
    print(f"Test Case 2 (No flags): {result_2}", file=sys.stderr) # Expected: {'total_flags_count': 0, ...}

    # Test Case 3: Single flag
    detected_3 = ['single_flag']
    result_3 = evaluate_total_flags_count(detected_3)
    print(f"Test Case 3 (Single flag): {result_3}", file=sys.stderr) # Expected: {'total_flags_count': 1, ...}

    # Test Case 4: Non-list input (error handling)
    try:
        result_4 = evaluate_total_flags_count(None)
        print(f"Test Case 4 (Non-list input): {result_4}", file=sys.stderr) # Expected: {'total_flags_count': 0, 'success': False, ...}
    except Exception as e:
        print(f"Test Case 4 (Non-list input) caught expected error: {e}", file=sys.stderr)
