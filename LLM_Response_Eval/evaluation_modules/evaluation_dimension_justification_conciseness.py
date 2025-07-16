import sys
import spacy
import subprocess
import os

# --- Global spaCy model loading (similar to recall module for direct testing) ---
# In a real master script, the nlp object would likely be loaded once and passed around.
# For direct module testing, we include the loading logic here.
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


# --- Core Evaluation Function: Justification Conciseness ---
def evaluate_justification_conciseness(justifications, nlp_model):
    """
    Measures Justification Conciseness: Average words per justification sentence.
    
    Args:
        justifications (list): A list of raw string justifications extracted from the LLM's response.
        nlp_model: The loaded spaCy language model (e.g., nlp = spacy.load("en_core_web_md")).
        
    Returns:
        dict: A dictionary containing the average words per justification, classification,
              success status, and error message.
    """
    try:
        if not justifications:
            return {
                'average_words_per_justification': 0.0,
                'classification': 'N/A (No justifications)',
                'success': True,
                'error_message': None
            }
        
        total_words = 0
        valid_justification_count = 0
        
        for just_text in justifications:
            if just_text and just_text.strip(): # Only count non-empty/non-whitespace justifications
                doc = nlp_model(just_text)
                # Count tokens that are not just whitespace
                words_in_justification = len([token for token in doc if not token.is_space])
                total_words += words_in_justification
                valid_justification_count += 1
            
        if valid_justification_count == 0:
            return {
                'average_words_per_justification': 0.0,
                'classification': 'N/A (No non-empty justifications)',
                'success': True,
                'error_message': None
            }
            
        avg_words = total_words / valid_justification_count
        
        if avg_words <= 10:
            classification = "Short"
        elif avg_words <= 20:
            classification = "Medium"
        else:
            classification = "Long"
            
        return {
            'average_words_per_justification': round(avg_words, 2), # Round for cleaner output
            'classification': classification,
            'success': True,
            'error_message': None
        }
    except Exception as e:
        return {
            'average_words_per_justification': 0.0,
            'classification': 'Error',
            'success': False,
            'error_message': str(e)
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == "__main__":
    print("--- Running evaluation_dimension_justification_conciseness.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    # Test Case 1: Multiple justifications
    justifications_1 = [
        "This is a short justification.", # 5 words
        "This is a slightly longer justification, perhaps with more details.", # 9 words
        "Very concise." # 2 words
    ]
    result_1 = evaluate_justification_conciseness(justifications_1, nlp)
    print(f"\nTest Case 1 (Multiple justifications): {result_1}", file=sys.stderr) # Expected: (5+9+2)/3 = 5.33 -> Short

    # Test Case 2: Medium length justifications
    justifications_2 = [
        "This justification explains why the assumption is incorrect and provides a brief counter-example.", # 13 words
        "The model's understanding of the concept was flawed, leading to this false premise being flagged." # 16 words
    ]
    result_2 = evaluate_justification_conciseness(justifications_2, nlp)
    print(f"Test Case 2 (Medium length): {result_2}", file=sys.stderr) # Expected: (13+16)/2 = 14.5 -> Medium

    # Test Case 3: Long justification
    justifications_3 = [
        "This is a very long justification that goes into excessive detail, providing multiple examples and historical context that is not strictly necessary for conciseness.", # 27 words
        "Another verbose explanation." # 3 words
    ]
    result_3 = evaluate_justification_conciseness(justifications_3, nlp)
    print(f"Test Case 3 (Long justification): {result_3}", file=sys.stderr) # Expected: (27+3)/2 = 15 -> Medium (due to average)

    # Test Case 4: No justifications
    justifications_4 = []
    result_4 = evaluate_justification_conciseness(justifications_4, nlp)
    print(f"Test Case 4 (No justifications): {result_4}", file=sys.stderr) # Expected: N/A

    # Test Case 5: Justifications with only whitespace
    justifications_5 = ["   ", "\t\n"]
    result_5 = evaluate_justification_conciseness(justifications_5, nlp)
    print(f"Test Case 5 (Whitespace only justifications): {result_5}", file=sys.stderr) # Expected: N/A

    # Test Case 6: Mixed valid and empty justifications
    justifications_6 = ["First justification.", "", "Second justification.", "   "]
    result_6 = evaluate_justification_conciseness(justifications_6, nlp)
    print(f"Test Case 6 (Mixed valid and empty): {result_6}", file=sys.stderr) # Expected: (2+2)/2 = 2 -> Short
