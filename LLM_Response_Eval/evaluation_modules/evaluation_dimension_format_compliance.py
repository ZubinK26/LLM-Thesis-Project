import re
import sys

# --- Core Evaluation Function: Format Compliance ---\
def evaluate_format_compliance(response_text):
    """
    Measures Format Compliance: Whether the response strictly followed the
    "Assumptions:" listing format before answering, providing granular details.

    Args:
        response_text (str): The full constrained LLM response text.

    Returns:
        dict: A dictionary containing compliance status (boolean), details (string),
              success status, and error message.
    """
    try:
        if not isinstance(response_text, str):
            return {
                'compliant': False,
                'details': 'Response is not a string.',
                'success': True,
                'error_message': None
            }

        lines = response_text.splitlines()
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
                'details': 'Response does not start with "Assumptions:".',
                'success': True,
                'error_message': None
            }
        
        # Find the index of "Assumptions:" and "Answer:"
        assumptions_idx = -1
        answer_idx = -1
        for i, line in enumerate(non_empty_lines):
            if line.lower().startswith("assumptions:"):
                assumptions_idx = i
            elif line.lower().startswith("answer:"):
                answer_idx = i
        
        if assumptions_idx == -1: # Should not happen due to first check, but for robustness
            return {
                'compliant': False,
                'details': 'Internal error: "Assumptions:" not found after initial check.',
                'success': False,
                'error_message': 'Logic error.'
            }

        if answer_idx == -1:
            return {
                'compliant': False,
                'details': 'Response is missing "Answer:" section.',
                'success': True,
                'error_message': None
            }

        if answer_idx <= assumptions_idx:
            return {
                'compliant': False,
                'details': '"Answer:" section appears before or on the same line as "Assumptions:".',
                'success': True,
                'error_message': None
            }

        # Extract lines between "Assumptions:" and "Answer:"
        flag_lines = non_empty_lines[assumptions_idx + 1:answer_idx]

        # 2. Check if all lines in the "Assumptions" block are numbered
        # Regex to match "1. Flag text. (Justification)"
        # This regex is from recall module, assuming consistency.
        numbered_item_pattern = re.compile(r'^\s*\d+\.\s*(.+)$') # Updated to just check for number.
        
        # Check for sequential numbering and correct format
        expected_number = 1
        for i, line in enumerate(flag_lines):
            match = numbered_item_pattern.match(line)
            if not match:
                return {
                    'compliant': False,
                    'details': f'Non-compliant flag format: Line {i+1} in Assumptions block is not a numbered item (e.g., "1. Flag text.").',
                    'success': True,
                    'error_message': None
                }
            
            # Extract the number to check sequential order
            line_number_str = line.strip().split('.')[0]
            try:
                current_number = int(line_number_str)
                if current_number != expected_number:
                    return {
                        'compliant': False,
                        'details': f'Non-sequential numbering in Assumptions block: Expected {expected_number}, found {current_number}.',
                        'success': True,
                        'error_message': None
                    }
                expected_number += 1
            except ValueError:
                # Should be caught by regex, but as a fallback
                return {
                    'compliant': False,
                    'details': f'Invalid number format in Assumptions block for line: "{line}".',
                    'success': True,
                    'error_message': None
                }

        # If we reach here, all checks passed
        return {
            'compliant': True,
            'details': 'Format is compliant.',
            'success': True,
            'error_message': None
        }

    except Exception as e:
        return {
            'compliant': False,
            'details': f'An unexpected error occurred during format compliance evaluation: {e}',
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_format_compliance.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Test Case 1: Fully compliant response
    response_1 = """Assumptions:
1. Flag one. (Justification)
2. Flag two.
Answer: This is the answer."""
    result_1 = evaluate_format_compliance(response_1)
    print(f"\nTest Case 1 (Compliant): {result_1}", file=sys.stderr) # Expected: compliant: True, details: "Format is compliant."

    # Test Case 2: Missing "Assumptions:"
    response_2 = """1. Flag one.
Answer: This is the answer."""
    result_2 = evaluate_format_compliance(response_2)
    print(f"Test Case 2 (Missing Assumptions:): {result_2}", file=sys.stderr) # Expected: compliant: False, details: "Response does not start with 'Assumptions:'."

    # Test Case 3: Missing "Answer:"
    response_3 = """Assumptions:
1. Flag one."""
    result_3 = evaluate_format_compliance(response_3)
    print(f"Test Case 3 (Missing Answer:): {result_3}", file=sys.stderr) # Expected: compliant: False, details: "Response is missing 'Answer:' section."

    # Test Case 4: Answer before Assumptions
    response_4 = """Answer: This is the answer.
Assumptions:
1. Flag one."""
    result_4 = evaluate_format_compliance(response_4)
    print(f"Test Case 4 (Answer before Assumptions): {result_4}", file=sys.stderr) # Expected: compliant: False, details: "'Answer:' section appears before or on the same line as 'Assumptions:'."

    # Test Case 5: Non-numbered item in assumptions
    response_5 = """Assumptions:
- Flag one.
Answer: This is the answer."""
    result_5 = evaluate_format_compliance(response_5)
    print(f"Test Case 5 (Non-numbered flag): {result_5}", file=sys.stderr) # Expected: compliant: False, details: "Non-compliant flag format: Line 1 in Assumptions block is not a numbered item..."

    # Test Case 6: Non-sequential numbering
    response_6 = """Assumptions:
1. Flag one.
3. Flag three.
Answer: This is the answer."""
    result_6 = evaluate_format_compliance(response_6)
    print(f"Test Case 6 (Non-sequential numbering): {result_6}", file=sys.stderr) # Expected: compliant: False, details: "Non-sequential numbering in Assumptions block: Expected 2, found 3."

    # Test Case 7: Empty response
    response_7 = ""
    result_7 = evaluate_format_compliance(response_7)
    print(f"Test Case 7 (Empty response): {result_7}", file=sys.stderr) # Expected: compliant: False, details: "Response is empty or only whitespace."

    # Test Case 8: Only "Assumptions:" and "Answer:" (no flags)
    response_8 = """Assumptions:

Answer: This is the answer."""
    result_8 = evaluate_format_compliance(response_8)
    print(f"Test Case 8 (No flags, compliant): {result_8}", file=sys.stderr) # Expected: compliant: True, details: "Format is compliant."

    # Test Case 9: Justification format variation (should still be compliant if numbered)
    response_9 = """Assumptions:
1. Flag with (justification).
Answer: This is the answer."""
    result_9 = evaluate_format_compliance(response_9)
    print(f"Test Case 9 (Justification format variation): {result_9}", file=sys.stderr) # Expected: compliant: True, details: "Format is compliant."

    # Test Case 10: No content after Assumptions: but no Answer:
    response_10 = """Assumptions:"""
    result_10 = evaluate_format_compliance(response_10)
    print(f"Test Case 10 (Assumptions only): {result_10}", file=sys.stderr) # Expected: compliant: False, details: "Response is missing 'Answer:' section."
