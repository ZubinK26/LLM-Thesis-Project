import re
import sys
import spacy
import subprocess
import os

# --- Global spaCy model loading for this module's direct testing ---
# In the master script, the nlp object is loaded once and passed/used globally.
# For this module to be runnable independently for testing, it needs its own nlp instance.
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("SpaCy 'en_core_web_md' model not found. Attempting to download...", file=sys.stderr)
    try:
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
        nlp = spacy.load("en_core_web_md")
        print("SpaCy 'en_core_web_md' model downloaded successfully.", file=sys.stderr)
    except Exception as e:
        print(f"Error downloading spaCy model: {e}. Please ensure you have pip and try running 'python -m spacy download en_core_web_md' manually.", file=sys.stderr)
        sys.exit(1)


# --- Helper Function: Text Normalization (Enhanced with spaCy) ---
def _normalize_text(text):
    """
    Normalizes text by lowercasing, removing punctuation, standardizing whitespace,
    removing stop words, and lemmatizing using spaCy.
    
    Args:
        text (str): The input string to normalize.
        
    Returns:
        str: The normalized string.
    """
    if not isinstance(text, str):
        return ""
    
    # Process text with spaCy
    doc = nlp(text.lower()) # Process lowercase text
    
    # Filter out punctuation, whitespace, and stop words; then lemmatize
    normalized_tokens = [
        token.lemma_ for token in doc 
        if not token.is_punct and not token.is_space and not token.is_stop
    ]
    
    # Join tokens back into a single string
    return " ".join(normalized_tokens).strip()


# --- Helper Function: Extract Constrained Flags and Justifications ---
def _extract_constrained_flags(response_text):
    """
    Extracts numbered assumption flags and their raw justifications from a constrained LLM response.
    Assumes format: "Assumptions:\n1. Flag. (Justification)\n2. Flag. (Justification)\nAnswer:..."
    
    Args:
        response_text (str): The full constrained LLM response text.
        
    Returns:
        tuple: A tuple containing:
            - list: Normalized detected flags.
            - list: Raw justifications corresponding to the flags.
    """
    detected_flags = []
    justifications = []
    in_assumptions_block = False
    
    if not isinstance(response_text, str):
        print(f"DEBUG (recall_module): _extract_constrained_flags - Input response_text is not a string: {type(response_text)}", file=sys.stderr)
        return [], []

    print(f"DEBUG (recall_module): _extract_constrained_flags - Input response_text (first 100 chars): {response_text[:100]}...", file=sys.stderr)

    lines = response_text.splitlines()
    
    for line in lines:
        stripped_line = line.strip()
        
        if stripped_line.lower().startswith("assumptions:"):
            in_assumptions_block = True
            print(f"DEBUG (recall_module): Entered assumptions block.", file=sys.stderr)
            continue # Skip the "Assumptions:" line itself

        if in_assumptions_block:
            if stripped_line.lower().startswith("answer:"):
                in_assumptions_block = False
                print(f"DEBUG (recall_module): Exited assumptions block (found Answer:).", file=sys.stderr)
                break # Stop processing lines once "Answer:" is found
            
            if not stripped_line:
                print(f"DEBUG (recall_module): Skipping empty line within block.", file=sys.stderr)
                continue # Skip empty lines within the block

            # Regex to match "1. Flag text. (Justification)"
            # Group 1: Number (unused here, but for validation)
            # Group 2: Flag text (before the first parenthesis)
            # Group 3: Justification text (inside parenthesis)
            match = re.match(r'^\s*\d+\.\s*([^(\n]+?)\s*\(([^)]+)\)$', stripped_line)
            if match:
                raw_flag_text = match.group(1).strip()
                raw_justification = match.group(2).strip()

                print(f"DEBUG (recall_module): Matched numbered item. Raw flag text: '{raw_flag_text}'", file=sys.stderr)
                
                # Remove trailing period from flag text if present
                if raw_flag_text.endswith('.'):
                    raw_flag_text = raw_flag_text[:-1]
                    print(f"DEBUG (recall_module): Removed trailing period. Cleaned raw flag: '{raw_flag_text}'", file=sys.stderr)
                
                normalized_flag = _normalize_text(raw_flag_text)
                
                detected_flags.append(normalized_flag)
                justifications.append(raw_justification)
                print(f"DEBUG (recall_module): Added flag: '{normalized_flag}', Justification: '{raw_justification}'", file=sys.stderr)
            else:
                print(f"DEBUG (recall_module): Line within block does not match numbered item pattern: '{stripped_line[:100]}'", file=sys.stderr)
                # If a line is in the assumptions block but doesn't match the numbered pattern,
                # it's not considered a flag for recall/precision purposes.
                # The format_compliance module will handle if this is a non-compliance.

    print(f"DEBUG (recall_module): Final detected flags: {detected_flags}", file=sys.stderr)
    print(f"DEBUG (recall_module): Final justifications: {justifications}", file=sys.stderr)
    return detected_flags, justifications


# --- Core Evaluation Function: Assumption Recall ---
def evaluate_assumption_recall(expected_flags, detected_flags):
    """
    Measures Assumption Recall: Proportion of expected false assumptions that the model actually flagged.
    
    Args:
        expected_flags (list): A list of normalized strings of ground truth assumptions.
        detected_flags (list): A list of normalized strings of assumptions detected from the LLM's response.
        
    Returns:
        dict: A dictionary containing the recall score, classification, success status, and error message.
    """
    try:
        if not expected_flags:
            # If there are no expected flags, recall is perfectly met (trivially true)
            return {
                'recall_score': 1.0,
                'classification': 'N/A (No expected flags)',
                'success': True,
                'error_message': None
            }
        
        # Convert to sets for efficient intersection
        expected_set = set(expected_flags)
        detected_set = set(detected_flags)

        correctly_recalled_flags = expected_set.intersection(detected_set)
        recall = len(correctly_recalled_flags) / len(expected_set)
        
        if recall >= 0.8:
            classification = "High"
        elif recall >= 0.5:
            classification = "Medium"
        else:
            classification = "Low"
            
        return {
            'recall_score': recall,
            'classification': classification,
            'success': True,
            'error_message': None
        }
    except Exception as e:
        return {
            'recall_score': 0.0, # Default to 0 on error
            'classification': 'Error',
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_recall.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Test Cases for _normalize_text
    print("\n--- Testing _normalize_text ---", file=sys.stderr)
    print(f"Original: 'The sky is always blue.', Normalized: '{_normalize_text('The sky is always blue.')}'", file=sys.stderr)
    print(f"Original: 'The Earth is flat.', Normalized: '{_normalize_text('The Earth is flat.')}'", file=sys.stderr)
    print(f"Original: 'Penguins are fish.', Normalized: '{_normalize_text('Penguins are fish.')}'", file=sys.stderr)
    print(f"Original: 'Water disappears when it evaporates.', Normalized: '{_normalize_text('Water disappears when it evaporates.')}'", file=sys.stderr)
    print(f"Original: 'Dinosaurs were small.', Normalized: '{_normalize_text('Dinosaurs were small.')}'", file=sys.stderr)
    print(f"Original: 'The human heart has only one chamber.', Normalized: '{_normalize_text('The human heart has only one chamber.')}'", file=sys.stderr)

    # Test Cases for _extract_constrained_flags (using updated _normalize_text)
    print("\n--- Testing _extract_constrained_flags ---", file=sys.stderr)
    sample_response_1 = """Assumptions:
1. The sky is always blue. (Incorrect, can be grey/red at times.)

Answer: The sky is blue due to Rayleigh scattering."""
    flags_1, just_1 = _extract_constrained_flags(sample_response_1)
    print(f"Detected Flags: {flags_1}", file=sys.stderr)
    print(f"Justifications: {just_1}", file=sys.stderr)

    sample_response_2 = """Assumptions:
1. All birds can fly. (Incorrect, penguins cannot fly.)
2. Penguins are fish. (Incorrect, penguins are birds.)

Answer: Not all birds can fly."""
    flags_2, just_2 = _extract_constrained_flags(sample_response_2)
    print(f"Detected Flags: {flags_2}", file=sys.stderr)
    print(f"Justifications: {just_2}", file=sys.stderr)

    sample_response_3 = """Assumptions:

Answer: The capital of France is Paris."""
    flags_3, just_3 = _extract_constrained_flags(sample_response_3)
    print(f"Detected Flags: {flags_3}", file=sys.stderr)
    print(f"Justifications: {just_3}", file=sys.stderr)

    sample_response_4 = """Assumptions:
The human heart has only one chamber. (False, it has four chambers.)

Answer: The human heart has four chambers."""
    flags_4, just_4 = _extract_constrained_flags(sample_response_4)
    print(f"Detected Flags: {flags_4}", file=sys.stderr)
    print(f"Justifications: {just_4}", file=sys.stderr)


    # Test Cases for evaluate_assumption_recall (using updated _normalize_text and _extract_constrained_flags)
    print("\n--- Testing evaluate_assumption_recall ---", file=sys.stderr)

    # Test Case 1: Perfect Recall (after normalization)
    expected_q002 = [_normalize_text("Earth is flat")] # Ground truth without "the"
    response_q002 = """Assumptions:
1. The Earth is flat. (Incorrect, it's a sphere.)

Answer: The Earth is not flat."""
    detected_q002, _ = _extract_constrained_flags(response_q002)
    result_q002 = evaluate_assumption_recall(expected_q002, detected_q002)
    print(f"Test Case Q002 (Recall, should be High): {result_q002}", file=sys.stderr)

    # Test Case 2: Partial Recall
    expected_partial = [_normalize_text("all birds can fly"), _normalize_text("penguins are fish"), _normalize_text("trees are blue")]
    response_partial = """Assumptions:
1. All birds can fly. (Incorrect)
2. Penguins are fish. (Incorrect)
Answer: ..."""
    detected_partial, _ = _extract_constrained_flags(response_partial)
    result_partial = evaluate_assumption_recall(expected_partial, detected_partial)
    print(f"Test Case Partial Recall (should be Medium/Low): {result_partial}", file=sys.stderr)

    # Test Case 3: No expected flags
    expected_none = []
    response_none = """Assumptions:
Answer: ..."""
    detected_none, _ = _extract_constrained_flags(response_none)
    result_none = evaluate_assumption_recall(expected_none, detected_none)
    print(f"Test Case No Expected (Recall): {result_none}", file=sys.stderr)
