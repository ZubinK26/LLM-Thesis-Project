import spacy

# Initialize the spaCy NLP pipeline once globally.
_spacy_nlp_compound_assumptions = None

def _initialize_spacy_nlp_compound_assumptions():
    """Initializes and returns the spaCy NLP pipeline for compound assumptions detection."""
    global _spacy_nlp_compound_assumptions
    if _spacy_nlp_compound_assumptions is None:
        try:
            print("Initializing spaCy NLP pipeline for compound assumptions...")
            _spacy_nlp_compound_assumptions = spacy.load("en_core_web_md")
            print("spaCy NLP pipeline for compound assumptions initialized successfully.")
        except OSError:
            print("Error: spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md")
            _spacy_nlp_compound_assumptions = None
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy for compound assumptions: {e}")
            _spacy_nlp_compound_assumptions = None
    return _spacy_nlp_compound_assumptions

def measure_spacy_compound_assumptions(text):
    """
    Detects and counts potential nested clauses (compound assumptions) in a text
    using spaCy's dependency parsing.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'nested_clauses_count': Integer count of detected nested clauses.
              - 'detected_clauses_info': List of strings describing each detected clause.
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'nested_clauses_count': 0,
        'detected_clauses_info': [],
        'success': False,
        'error_message': None
    }

    nlp = _initialize_spacy_nlp_compound_assumptions()
    if nlp is None:
        results['error_message'] = "spaCy NLP pipeline failed to initialize for compound assumptions."
        return results

    try:
        doc = nlp(text)

        # Define common dependency tags that indicate subordinate clauses
        # These tags typically mark the root of a clause that is embedded within another clause.
        # - advcl: Adverbial clause modifier (e.g., "If you go, I will follow.")
        # - ccomp: Complement clause (e.g., "He said that he would come.")
        # - acl: Clausal modifier of noun (e.g., "The man who came...")
        # - relcl: Relative clause modifier (a specific type of acl, e.g., "The book that I read...")
        # - xcomp: Open clausal complement (e.g., "He wants to go." - often infinitival clauses)
        # - csubj: Clausal subject (e.g., "That he was late was obvious.")
        # - csubjpass: Clausal passive subject
        subordinate_clause_deps = ["advcl", "ccomp", "acl", "relcl", "xcomp", "csubj", "csubjpass"]
        
        detected_clauses = []
        for token in doc:
            if token.dep_ in subordinate_clause_deps:
                # Attempt to capture the full clause for better understanding
                # This is a heuristic; getting the precise span of a clause can be complex.
                # Here, we'll show the head of the clause and its dependency.
                detected_clauses.append(f"'{token.text}' (Dependency: {token.dep_}, Head: '{token.head.text}')")
        
        results['nested_clauses_count'] = len(detected_clauses)
        results['detected_clauses_info'] = detected_clauses
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during spaCy compound assumptions processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Compound Assumptions (spaCy Dependency) Test (Standalone) ---")

    # Test Case 1: Sentence with a clear adverbial clause
    test_text_1 = "If you study hard, you will succeed in your exams."
    print(f"\nAnalyzing Text 1: '{test_text_1}'")
    results_1 = measure_spacy_compound_assumptions(test_text_1)
    if results_1['success']:
        print("\nResults for Text 1:")
        print(f"  Nested Clauses Count: {results_1['nested_clauses_count']}")
        print(f"  Detected Clauses Info: {results_1['detected_clauses_info']}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: Sentence with a complement clause
    test_text_2 = "She believes that he will arrive soon."
    print(f"\nAnalyzing Text 2: '{test_text_2}'")
    results_2 = measure_spacy_compound_assumptions(test_text_2)
    if results_2['success']:
        print("\nResults for Text 2:")
        print(f"  Nested Clauses Count: {results_2['nested_clauses_count']}")
        print(f"  Detected Clauses Info: {results_2['detected_clauses_info']}")
    else:
        print(f"  Error: {results_2['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Sentence with no obvious nested clauses
    test_text_3 = "The quick brown fox jumps over the lazy dog."
    print(f"\nAnalyzing Text 3: '{test_text_3}'")
    results_3 = measure_spacy_compound_assumptions(test_text_3)
    if results_3['success']:
        print("\nResults for Text 3:")
        print(f"  Nested Clauses Count: {results_3['nested_clauses_count']}")
        print(f"  Detected Clauses Info: {results_3['detected_clauses_info']}")
    else:
        print(f"  Error: {results_3['error_message']}")