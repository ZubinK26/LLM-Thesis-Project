import re
import sys

# --- Core Evaluation Function: Format Compliance ---
def evaluate_format_compliance(response_text):
    """
    Measures Format Compliance: Whether the response strictly followed the
    "Assumptions:" listing format before answering.
    
    Args:
        response_text (str): The full constrained LLM response text.
        
    Returns:
        dict: A dictionary containing compliance status, details, success status, and error message.
    """
    try:
        if not isinstance(response_text, str):
            return {
                'compliant': False,
                'details': 'Response is not a string.',
                'success': True, # Evaluation ran successfully, just found non-string input
                'error_message': None
            }

        # Use splitlines() for robust splitting across different OS newline conventions
        lines = response_text.splitlines()
        
        # Remove empty lines for initial checks
        non_empty_lines = [line.strip() for line in lines if line.strip()]

        if not non_empty_lines:
            return {
                'compliant': False,
                'details': 'Response is empty or only whitespace.',
                'success': True,
                'error_message': None
            }

        # 1. Check for "Assumptions:" as the first significant line
        if not non_empty_lines[0].lower().startswith("assumptions:"):
            return {
                'compliant': False,
                'details': f"Does not start with 'Assumptions:'. Found: '{non_empty_lines[0][:50]}...'",
                'success': True,
                'error_message': None
            }
        
        # Find the start and end of the assumptions block
        assumptions_start_index = -1
        answer_start_index = -1
        
        for i, line in enumerate(lines):
            if line.strip().lower().startswith("assumptions:"):
                assumptions_start_index = i
            if line.strip().lower().startswith("answer:"):
                answer_start_index = i
                break # Found the answer, no need to search further

        # If "Assumptions:" was found
        if assumptions_start_index != -1:
            # Extract the content between "Assumptions:" and "Answer:" (or end of text)
            assumptions_content_lines = []
            if answer_start_index != -1:
                # Content is between assumptions_start_index + 1 and answer_start_index
                assumptions_content_lines = lines[assumptions_start_index + 1 : answer_start_index]
            else:
                # Content is from assumptions_start_index + 1 to the end of the response
                assumptions_content_lines = lines[assumptions_start_index + 1 :]
            
            # Filter out empty lines for checking numbering
            assumptions_content_non_empty = [l.strip() for l in assumptions_content_lines if l.strip()]

            # 2. Check for numbered list items within the assumptions block
            if assumptions_content_non_empty:
                numbered_lines_found = False
                expected_num = 1
                for line_content in assumptions_content_non_empty:
                    num_match = re.match(r'^\s*(\d+)\.\s*(.*)$', line_content)
                    if num_match:
                        numbered_lines_found = True
                        current_num = int(num_match.group(1))
                        if current_num != expected_num:
                            return {
                                'compliant': False,
                                'details': f"Numbered list is not sequential. Expected {expected_num}, got {current_num}.",
                                'success': True,
                                'error_message': None
                            }
                        expected_num += 1
                    else:
                        # If a line exists and is not numbered, and it's not the first line after "Assumptions:"
                        # and we haven't found any numbered items yet, it's a non-compliance.
                        # This handles cases where there's text before the first numbered item.
                        if not numbered_lines_found:
                             return {
                                'compliant': False,
                                'details': f"Content found in assumptions block before first numbered item or non-numbered item: '{line_content[:50]}...'",
                                'success': True,
                                'error_message': None
                            }
                
                # If we entered the assumptions content section but found no numbered lines at all
                if not numbered_lines_found:
                    return {
                        'compliant': False,
                        'details': "Assumptions block contains content but no numbered list items.",
                        'success': True,
                        'error_message': None
                    }
            elif answer_start_index == -1: # If no assumptions content and no "Answer:" keyword found
                 return {
                    'compliant': False,
                    'details': "No 'Answer:' section found after 'Assumptions:' and no content in between.",
                    'success': True,
                    'error_message': None
                }
            # If assumptions_content_non_empty is empty, and Answer: was found, it's compliant (e.g., Assumptions:\n\nAnswer:)
            # This is handled by passing the above checks.

        # 3. Check for "Answer:" section
        if answer_start_index == -1:
            return {
                'compliant': False,
                'details': "No 'Answer:' section found.",
                'success': True,
                'error_message': None
            }

        return {
            'compliant': True,
            'details': 'Format is compliant.',
            'success': True,
            'error_message': None
        }
    except Exception as e:
        return {
            'compliant': False,
            'details': 'An error occurred during format compliance evaluation.',
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_format_compliance.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Test Case 1: Fully Compliant
    response_1 = """Assumptions:
1. The sky is always blue. (Incorrect)
2. Birds can fly.
Answer: This is the answer."""
    result_1 = evaluate_format_compliance(response_1)
    print(f"\nTest Case 1 (Fully Compliant): {result_1}", file=sys.stderr) # Expected: True

    # Test Case 2: Missing "Assumptions:"
    response_2 = """1. The sky is always blue.
Answer: This is the answer."""
    result_2 = evaluate_format_compliance(response_2)
    print(f"Test Case 2 (Missing Assumptions:): {result_2}", file=sys.stderr) # Expected: False

    # Test Case 3: Missing numbered list
    response_3 = """Assumptions:
Some text here.
Answer: This is the answer."""
    result_3 = evaluate_format_compliance(response_3)
    print(f"Test Case 3 (Missing numbered list): {result_3}", file=sys.stderr) # Expected: False

    # Test Case 4: Non-sequential numbering
    response_4 = """Assumptions:
1. Flag one.
3. Flag three.
Answer: This is the answer."""
    result_4 = evaluate_format_compliance(response_4)
    print(f"Test Case 4 (Non-sequential numbering): {result_4}", file=sys.stderr) # Expected: False

    # Test Case 5: Missing "Answer:"
    response_5 = """Assumptions:
1. Flag one."""
    result_5 = evaluate_format_compliance(response_5)
    print(f"Test Case 5 (Missing Answer:): {result_5}", file=sys.stderr) # Expected: False

    # Test Case 6: Empty response
    response_6 = ""
    result_6 = evaluate_format_compliance(response_6)
    print(f"Test Case 6 (Empty response): {result_6}", file=sys.stderr) # Expected: False

    # Test Case 7: Only "Assumptions:" and "Answer:" (no flags)
    response_7 = """Assumptions:

Answer: This is the answer."""
    result_7 = evaluate_format_compliance(response_7)
    print(f"Test Case 7 (No flags, compliant): {result_7}", file=sys.stderr) # Expected: True

    # Test Case 8: Preamble before "Assumptions:"
    response_8 = """Hello, this is a preamble.
Assumptions:
1. Flag one.
Answer: This is the answer."""
    result_8 = evaluate_format_compliance(response_8)
    print(f"Test Case 8 (Preamble before Assumptions:): {result_8}", file=sys.stderr) # Expected: False (because "Assumptions:" not first non-empty)

    # Test Case 9: Justification format variation (should still be compliant if numbered)
    response_9 = """Assumptions:
1. Flag with (justification).
Answer: This is the answer."""
    result_9 = evaluate_format_compliance(response_9)
    print(f"Test Case 9 (Justification format variation): {result_9}", file=sys.stderr) # Expected: True

    # Test Case 10: No content after Assumptions: but no Answer:
    response_10 = """Assumptions:"""
    result_10 = evaluate_format_compliance(response_10)
    print(f"Test Case 10 (No content after Assumptions: no Answer:): {result_10}", file=sys.stderr) # Expected: False
