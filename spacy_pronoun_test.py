import spacy

# Initialize the spaCy NLP pipeline once globally.
_spacy_nlp_pronoun_detection = None

def _initialize_spacy_nlp_pronoun_detection():
    """Initializes and returns the spaCy NLP pipeline for pronoun detection."""
    global _spacy_nlp_pronoun_detection
    if _spacy_nlp_pronoun_detection is None:
        try:
            print("Initializing spaCy NLP pipeline for pronoun detection...")
            _spacy_nlp_pronoun_detection = spacy.load("en_core_web_md")
            print("spaCy NLP pipeline for pronoun detection initialized successfully.")
        except OSError:
            print("Error: spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md")
            _spacy_nlp_pronoun_detection = None
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy for pronoun detection: {e}")
            _spacy_nlp_pronoun_detection = None
    return _spacy_nlp_pronoun_detection

def measure_spacy_pronoun_detection(text):
    """
    Detects pronouns in a given text using spaCy.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'pronoun_count': Integer count of detected pronouns.
              - 'detected_pronouns': List of strings, e.g., "'She' (Lemma: she, POS: PRON)".
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'pronoun_count': 0,
        'detected_pronouns': [],
        'success': False,
        'error_message': None
    }

    nlp = _initialize_spacy_nlp_pronoun_detection()
    if nlp is None:
        results['error_message'] = "spaCy NLP pipeline failed to initialize for pronoun detection."
        return results

    try:
        doc = nlp(text)
        
        for token in doc:
            if token.pos_ == "PRON":
                results['detected_pronouns'].append(f"'{token.text}' (Lemma: {token.lemma_}, POS: {token.pos_}, Morph: {token.morph})")
        
        results['pronoun_count'] = len(results['detected_pronouns'])
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during spaCy pronoun detection processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Ambiguity (spaCy Pronoun Detection) Test (Standalone) ---")

    # Test Case 1: Simple sentence with pronouns
    test_text_1 = "She quickly ran to him, but he wasn't there."
    print(f"\nAnalyzing Text 1: '{test_text_1}'")
    results_1 = measure_spacy_pronoun_detection(test_text_1)
    if results_1['success']:
        print("\nResults for Text 1:")
        print(f"  Pronoun Count: {results_1['pronoun_count']}")
        print(f"  Detected Pronouns: {results_1['detected_pronouns']}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: Sentence with various types of pronouns and other POS tags
    test_text_2 = "They saw themselves in the mirror. What did it mean to them?"
    print(f"\nAnalyzing Text 2: '{test_text_2}'")
    results_2 = measure_spacy_pronoun_detection(test_text_2)
    if results_2['success']:
        print("\nResults for Text 2:")
        print(f"  Pronoun Count: {results_2['pronoun_count']}")
        print(f"  Detected Pronouns: {results_2['detected_pronouns']}")
    else:
        print(f"  Error: {results_2['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Sentence with no obvious pronouns
    test_text_3 = "The cat sat on the mat."
    print(f"\nAnalyzing Text 3: '{test_text_3}'")
    results_3 = measure_spacy_pronoun_detection(test_text_3)
    if results_3['success']:
        print("\nResults for Text 3:")
        print(f"  Pronoun Count: {results_3['pronoun_count']}")
        print(f"  Detected Pronouns: {results_3['detected_pronouns']}")
    else:
        print(f"  Error: {results_3['error_message']}")