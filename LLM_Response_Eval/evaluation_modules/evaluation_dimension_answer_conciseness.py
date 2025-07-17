import sys
import spacy
import re # For extracting the answer section

# --- Global spaCy model loading for this module's direct testing ---
# In the master script, the nlp object is loaded once and passed/used globally.
# For this module to be runnable independently for testing, it needs its own nlp instance.
# This block is similar to what's in recall and conciseness modules.
try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    print("SpaCy 'en_core_web_md' model not found. Attempting to download...", file=sys.stderr)
    try:
        # Note: In a production environment, spacy.download should be run once during setup.
        # This is here for convenience during direct module testing.
        import subprocess
        subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
        nlp = spacy.load("en_core_web_md")
        print("SpaCy 'en_core_web_md' model downloaded successfully.", file=sys.stderr)
    except Exception as e:
        print(f"Error downloading spaCy model: {e}. Please ensure you have pip and try running 'python -m spacy download en_core_web_md' manually.", file=sys.stderr)
        sys.exit(1)


# --- Helper to extract the Answer section ---
def _extract_answer_text(response_text: str) -> str:
    """
    Extracts the text following 'Answer:' in the constrained response.
    """
    answer_match = re.search(r"Answer:\s*(.*)", response_text, re.DOTALL | re.IGNORECASE)
    if answer_match:
        return answer_match.group(1).strip()
    return ""


# --- Core Evaluation Function: Answer Conciseness ---
def evaluate_answer_conciseness(constrained_response_text: str, nlp_model) -> dict:
    """
    Measures Answer Conciseness: Word and sentence count of the LLM's final answer.

    Args:
        constrained_response_text (str): The full constrained LLM response text.
        nlp_model: The loaded spaCy language model (e.g., nlp = spacy.load("en_core_web_md")).

    Returns:
        dict: A dictionary containing the word count, sentence count, and classification
              for the answer section, success status, and error message.
    """
    try:
        answer_text = _extract_answer_text(constrained_response_text)

        if not answer_text:
            return {
                'word_count': 0,
                'sentence_count': 0,
                'classification': 'N/A (No answer text)',
                'success': True,
                'error_message': None
            }

        doc = nlp(answer_text)
        word_count = len([token for token in doc if token.is_alpha]) # Count only alphabetic words
        sentence_count = len(list(doc.sents))

        # Define conciseness classifications based on word count
        if word_count <= 10:
            classification = "Very Short"
        elif word_count <= 30:
            classification = "Short"
        elif word_count <= 60:
            classification = "Medium"
        else:
            classification = "Long"

        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'classification': classification,
            'success': True,
            'error_message': None
        }

    except Exception as e:
        return {
            'word_count': 'N/A',
            'sentence_count': 'N/A',
            'classification': 'N/A',
            'success': False,
            'error_message': f"Error evaluating answer conciseness: {e}"
        }

# --- If this module is run directly (for testing purposes) ---
if __name__ == '__main__':
    print("--- Running evaluation_dimension_answer_conciseness.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    test_response_1 = """Assumptions:
1. Flag one.
Answer: This is a very short answer.""" # 6 words
    
    test_response_2 = """Assumptions:
1. Flag two.
Answer: This is a slightly longer answer that provides a bit more detail, but still aims for conciseness. It has multiple sentences. This is the second sentence.""" # 28 words, 3 sentences

    test_response_3 = """Assumptions:
1. Flag three.
Answer: This is a considerably long answer that delves into significant detail, providing extensive background information and multiple examples to fully elaborate on the topic. It might even include some caveats and additional context to ensure comprehensive understanding for the reader, which can make it quite verbose and less concise, potentially impacting user experience negatively if brevity is desired. This is a very long sentence. And another one. And another. And another. And another. And another. And another. And another.""" # 86 words, 9 sentences

    test_response_4 = """Assumptions:
1. Flag four.""" # Missing Answer: section

    test_response_5 = """Assumptions:
1. Flag five.
Answer: """ # Empty answer section

    print(f"\nTest Response 1 (Very Short): '{test_response_1.splitlines()[-1]}'")
    print(f"Conciseness: {evaluate_answer_conciseness(test_response_1, nlp)}")
    print("-" * 30)

    print(f"\nTest Response 2 (Short): '{test_response_2.splitlines()[-2]}'")
    print(f"Conciseness: {evaluate_answer_conciseness(test_response_2, nlp)}")
    print("-" * 30)

    print(f"\nTest Response 3 (Long): '{test_response_3.splitlines()[-2]}'")
    print(f"Conciseness: {evaluate_answer_conciseness(test_response_3, nlp)}")
    print("-" * 30)

    print(f"\nTest Response 4 (Missing Answer:): '{test_response_4.splitlines()[-1]}'")
    print(f"Conciseness: {evaluate_answer_conciseness(test_response_4, nlp)}")
    print("-" * 30)

    print(f"\nTest Response 5 (Empty Answer:): '{test_response_5.splitlines()[-1]}'")
    print(f"Conciseness: {evaluate_answer_conciseness(test_response_5, nlp)}")
    print("-" * 30)
