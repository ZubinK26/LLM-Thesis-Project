import textstat
import sys

def evaluate_response_readability(response_text: str) -> dict:
    """
    Measures the readability and complexity of the LLM's response using various
    textstat metrics.

    Args:
        response_text (str): The text of the LLM's response (e.g., unconstrained response).

    Returns:
        dict: A dictionary containing various readability scores, success status, and error message.
    """
    try:
        if not isinstance(response_text, str) or not response_text.strip():
            return {
                'flesch_reading_ease': 0.0,
                'flesch_kincaid_grade': 0.0,
                'dale_chall_readability': 0.0,
                'smog_index': 0.0,
                'coleman_liau_index': 0.0,
                'automated_readability_index': 0.0,
                'linsear_write_formula': 0.0,
                'gunning_fog_index': 0.0,
                'text_length_words': 0,
                'text_length_sentences': 0,
                'success': True,
                'error_message': "Empty or invalid response text."
            }

        # Calculate various readability scores
        flesch_ease = textstat.flesch_reading_ease(response_text)
        flesch_kincaid = textstat.flesch_kincaid_grade(response_text)
        dale_chall = textstat.dale_chall_readability_score(response_text)
        smog = textstat.smog_index(response_text)
        coleman_liau = textstat.coleman_liau_index(response_text)
        ari = textstat.automated_readability_index(response_text)
        linsear = textstat.linsear_write_formula(response_text)
        gunning_fog = textstat.gunning_fog(response_text)

        # Basic text length metrics
        word_count = textstat.lexicon_count(response_text, removepunct=True)
        sentence_count = textstat.sentence_count(response_text)

        return {
            'flesch_reading_ease': round(flesch_ease, 2),
            'flesch_kincaid_grade': round(flesch_kincaid, 2),
            'dale_chall_readability': round(dale_chall, 2),
            'smog_index': round(smog, 2),
            'coleman_liau_index': round(coleman_liau, 2),
            'automated_readability_index': round(ari, 2),
            'linsear_write_formula': round(linsear, 2),
            'gunning_fog_index': round(gunning_fog, 2),
            'text_length_words': word_count,
            'text_length_sentences': sentence_count,
            'success': True,
            'error_message': None
        }

    except Exception as e:
        # Catch specific errors if textstat fails (e.g., too short text for some metrics)
        # textstat can raise ValueError for very short texts for some metrics.
        # We'll return default values and an error message.
        return {
            'flesch_reading_ease': 'N/A',
            'flesch_kincaid_grade': 'N/A',
            'dale_chall_readability': 'N/A',
            'smog_index': 'N/A',
            'coleman_liau_index': 'N/A',
            'automated_readability_index': 'N/A',
            'linsear_write_formula': 'N/A',
            'gunning_fog_index': 'N/A',
            'text_length_words': 'N/A',
            'text_length_sentences': 'N/A',
            'success': False,
            'error_message': f"Error evaluating readability: {e}"
        }

# Example Usage (for direct testing of this module)
if __name__ == '__main__':
    print("--- Running evaluation_dimension_response_readability.py directly for testing ---", file=sys.stderr)
    print("This module is intended to be imported by a master evaluation script.", file=sys.stderr)

    test_response_1 = "The quick brown fox jumps over the lazy dog. This is a simple sentence."
    test_response_2 = "Photosynthesis is the process used by plants, algae and cyanobacteria to convert light energy into chemical energy, through a process that converts water and carbon dioxide into sugars and oxygen."
    test_response_3 = "The inherent complexity of quantum mechanics often necessitates a nuanced understanding of wave-particle duality and probabilistic interpretations, which can be challenging for novices."
    test_response_4 = "" # Empty string
    test_response_5 = "Hello." # Very short string

    print(f"\nTest Response 1: '{test_response_1}'")
    print(f"Readability: {evaluate_response_readability(test_response_1)}")
    print("-" * 30)

    print(f"\nTest Response 2: '{test_response_2}'")
    print(f"Readability: {evaluate_response_readability(test_response_2)}")
    print("-" * 30)

    print(f"\nTest Response 3: '{test_response_3}'")
    print(f"Readability: {evaluate_response_readability(test_response_3)}")
    print("-" * 30)

    print(f"\nTest Response 4 (Empty): '{test_response_4}'")
    print(f"Readability: {evaluate_response_readability(test_response_4)}")
    print("-" * 30)

    print(f"\nTest Response 5 (Very Short): '{test_response_5}'")
    print(f"Readability: {evaluate_response_readability(test_response_5)}")
    print("-" * 30)
