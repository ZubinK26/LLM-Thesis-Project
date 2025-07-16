import Levenshtein # Assuming 'python-Levenshtein' library is installed
import spacy

# Initialize the spaCy NLP pipeline once globally.
_spacy_nlp_paraphrase_distance = None

def _initialize_spacy_nlp_paraphrase_distance():
    """Initializes and returns the spaCy NLP pipeline for paraphrase distance tokenization."""
    global _spacy_nlp_paraphrase_distance
    if _spacy_nlp_paraphrase_distance is None:
        try:
            print("Initializing spaCy NLP pipeline for paraphrase distance...")
            _spacy_nlp_paraphrase_distance = spacy.load("en_core_web_md")
            print("spaCy NLP pipeline for paraphrase distance initialized successfully.")
        except OSError:
            print("Error: spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md")
            _spacy_nlp_paraphrase_distance = None
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy for paraphrase distance: {e}")
            _spacy_nlp_paraphrase_distance = None
    return _spacy_nlp_paraphrase_distance

def measure_paraphrase_distance(text1, text2, level="word"):
    """
    Calculates the Levenshtein distance between two texts.

    Args:
        text1 (str): The first text (e.g., original query).
        text2 (str): The second text (e.g., paraphrase).
        level (str): 'word' for word-level Levenshtein distance (recommended for paraphrase),
                     or 'char' for character-level Levenshtein distance.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'word_level_distance': Float, Levenshtein distance at word level (if 'word' level requested).
              - 'char_level_distance': Float, Levenshtein distance at character level (if 'char' level requested).
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'word_level_distance': -1, # Default to -1 or None to indicate not calculated
        'char_level_distance': -1, # Default to -1 or None
        'success': False,
        'error_message': None
    }

    nlp = None
    if level == "word":
        nlp = _initialize_spacy_nlp_paraphrase_distance()
        if nlp is None:
            results['error_message'] = "spaCy NLP pipeline failed to initialize for word-level paraphrase distance."
            return results

    try:
        distance = -1 # Initialize distance to an invalid value

        if level == "word":
            # Normalize and tokenize texts
            doc1 = nlp(text1.lower())
            doc2 = nlp(text2.lower())
            seq1 = [token.text for token in doc1]
            seq2 = [token.text for token in doc2]
            
            distance = Levenshtein.distance(seq1, seq2)
            results['word_level_distance'] = distance
            
        elif level == "char":
            # Normalize texts (lowercase)
            seq1 = text1.lower()
            seq2 = text2.lower()
            
            distance = Levenshtein.distance(seq1, seq2)
            results['char_level_distance'] = distance
            
        else:
            results['error_message'] = "Invalid 'level' specified. Must be 'word' or 'char'."
            return results

        results['success'] = True

    except Levenshtein.Error as e:
        results['error_message'] = f"Levenshtein calculation error: {e}"
        results['success'] = False
    except Exception as e:
        results['error_message'] = f"An unexpected error occurred during paraphrase distance calculation: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Paraphrase Distance (Levenshtein) Dimension Test (Standalone) ---")

    # Test Case 1: Identical sentences (distance should be 0)
    text_a = "The cat sat on the mat."
    text_b = "The cat sat on the mat."
    print(f"\nComparing: '{text_a}' vs '{text_b}'")
    results_word = measure_paraphrase_distance(text_a, text_b, level="word")
    results_char = measure_paraphrase_distance(text_a, text_b, level="char")

    if results_word['success'] and results_char['success']:
        print("\nResults:")
        print(f"  Word-level Levenshtein Distance: {results_word['word_level_distance']}")
        print(f"  Character-level Levenshtein Distance: {results_char['char_level_distance']}")
    else:
        print(f"  Word-level Error: {results_word['error_message']}")
        print(f"  Char-level Error: {results_char['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: Slight difference (one word change)
    text_c = "The dog sat on the mat."
    print(f"\nComparing: '{text_a}' vs '{text_c}'")
    results_word = measure_paraphrase_distance(text_a, text_c, level="word")
    results_char = measure_paraphrase_distance(text_a, text_c, level="char")

    if results_word['success'] and results_char['success']:
        print("\nResults:")
        print(f"  Word-level Levenshtein Distance: {results_word['word_level_distance']}")
        print(f"  Character-level Levenshtein Distance: {results_char['char_level_distance']}")
    else:
        print(f"  Word-level Error: {results_word['error_message']}")
        print(f"  Char-level Error: {results_char['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Different lengths
    text_e = "The cat."
    print(f"\nComparing: '{text_a}' vs '{text_e}'")
    results_word = measure_paraphrase_distance(text_a, text_e, level="word")
    results_char = measure_paraphrase_distance(text_a, text_e, level="char")

    if results_word['success'] and results_char['success']:
        print("\nResults:")
        print(f"  Word-level Levenshtein Distance: {results_word['word_level_distance']}")
        print(f"  Character-level Levenshtein Distance: {results_char['char_level_distance']}")
    else:
        print(f"  Word-level Error: {results_word['error_message']}")
        print(f"  Char-level Error: {results_char['error_message']}")