import spacy

# Initialize the spaCy NLP pipeline once globally or pass it to the function.
# This helps avoid re-initializing the pipeline for every call if used in a loop.
_spacy_nlp_voice = None

def _initialize_spacy_nlp_voice():
    """Initializes and returns the spaCy NLP pipeline for voice detection."""
    global _spacy_nlp_voice
    if _spacy_nlp_voice is None:
        try:
            print("Initializing spaCy NLP pipeline for voice detection...")
            _spacy_nlp_voice = spacy.load("en_core_web_md")
            print("spaCy NLP pipeline for voice detection initialized successfully.")
        except OSError:
            print("Error: spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md")
            _spacy_nlp_voice = None
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy for voice detection: {e}")
            _spacy_nlp_voice = None
    return _spacy_nlp_voice

def measure_spacy_voice_detection(text):
    """
    Detects the voice (active or passive) of sentences in a given text
    and counts the number of passive sentences using spaCy's dependency parse.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'voice_classification': 'Passive' if any passive sentences are found, 'Active' otherwise.
              - 'passive_sentence_count': Integer count of sentences identified as passive.
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'voice_classification': 'Active', # Default to active
        'passive_sentence_count': 0,
        'success': False,
        'error_message': None
    }

    nlp = _initialize_spacy_nlp_voice()
    if nlp is None:
        results['error_message'] = "spaCy NLP pipeline failed to initialize for voice detection."
        return results

    try:
        doc = nlp(text)
        
        passive_count = 0
        for sent in doc.sents:
            # Check for passive voice indicators within the sentence
            # 'nsubjpass': nominal subject of a passive verb
            # 'auxpass': passive auxiliary verb (e.g., 'is', 'was', 'been' used in passive constructions)
            is_passive_sentence = False
            for token in sent:
                if token.dep_ == "nsubjpass" or token.dep_ == "auxpass":
                    is_passive_sentence = True
                    break # Found a passive indicator, no need to check other tokens in this sentence
            if is_passive_sentence:
                passive_count += 1
        
        results['passive_sentence_count'] = passive_count
        if passive_count > 0:
            results['voice_classification'] = 'Passive'
        else:
            results['voice_classification'] = 'Active' # Explicitly set if no passive found
        
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during spaCy voice detection processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Semantic Complexity (spaCy Voice Detection) Test (Standalone) ---")

    # Test Case 1: Passive voice
    test_text_1 = "The function is assumed to be differentiable everywhere."
    print(f"\nAnalyzing Text 1: '{test_text_1}'")
    results_1 = measure_spacy_voice_detection(test_text_1)
    if results_1['success']:
        print("\nResults for Text 1:")
        print(f"  Voice Classification: {results_1['voice_classification']}")
        print(f"  Passive Sentence Count: {results_1['passive_sentence_count']}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: Active voice
    test_text_2 = "The student solved the problem quickly."
    print(f"\nAnalyzing Text 2: '{test_text_2}'")
    results_2 = measure_spacy_voice_detection(test_text_2)
    if results_2['success']:
        print("\nResults for Text 2:")
        print(f"  Voice Classification: {results_2['voice_classification']}")
        print(f"  Passive Sentence Count: {results_2['passive_sentence_count']}")
    else:
        print(f"  Error: {results_2['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Mixed voices
    test_text_3 = "The ball was thrown by the boy, and it hit the window."
    print(f"\nAnalyzing Text 3: '{test_text_3}'")
    results_3 = measure_spacy_voice_detection(test_text_3)
    if results_3['success']:
        print("\nResults for Text 3:")
        print(f"  Voice Classification: {results_3['voice_classification']}")
        print(f"  Passive Sentence Count: {results_3['passive_sentence_count']}")
    else:
        print(f"  Error: {results_3['error_message']}")
