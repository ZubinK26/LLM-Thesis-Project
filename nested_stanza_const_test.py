import stanza

# Initialize the Stanza NLP pipeline once globally.
_stanza_nlp_compound_assumptions = None

def _initialize_stanza_nlp_compound_assumptions():
    """Initializes and returns the Stanza NLP pipeline for compound assumptions detection."""
    global _stanza_nlp_compound_assumptions
    if _stanza_nlp_compound_assumptions is None:
        try:
            print("Initializing Stanza NLP pipeline for compound assumptions...")
            _stanza_nlp_compound_assumptions = stanza.Pipeline(
                lang='en',
                processors='tokenize,mwt,pos,constituency',
                use_gpu=False, # Set to True if you have a compatible GPU and drivers
                verbose=False # Suppress verbose loading messages for cleaner output
            )
            print("Stanza NLP pipeline for compound assumptions initialized successfully.")
        except Exception as e:
            print(f"Error initializing Stanza NLP pipeline for compound assumptions: {e}")
            _stanza_nlp_compound_assumptions = None
    return _stanza_nlp_compound_assumptions

def count_subordinate_clauses_stanza(node):
    """Recursively counts SBAR (subordinate clause) nodes in a constituency parse tree."""
    count = 1 if node.label == "SBAR" else 0
    for child in node.children:
        count += count_subordinate_clauses_stanza(child)
    return count

def measure_stanza_compound_assumptions(text):
    """
    Measures the count of nested SBAR (subordinate) clauses using Stanza's constituency parser.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'nested_sbar_count': Integer count of SBAR (subordinate clause) nodes.
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'nested_sbar_count': 0,
        'success': False,
        'error_message': None
    }

    nlp = _initialize_stanza_nlp_compound_assumptions()
    if nlp is None:
        results['error_message'] = "Stanza NLP pipeline failed to initialize for compound assumptions."
        return results

    try:
        doc = nlp(text)
        if not doc.sentences:
            results['error_message'] = "No sentences detected in the text by Stanza."
            return results

        # Assuming we analyze the first sentence for simplicity, as per previous examples.
        # For multi-sentence queries, you might want to sum these metrics across sentences.
        tree = doc.sentences[0].constituency

        results['nested_sbar_count'] = count_subordinate_clauses_stanza(tree)
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during Stanza compound assumptions processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Compound Assumptions (Stanza Constituency) Dimension Test (Standalone) ---")

    # Ensure Stanza models are downloaded if not already present
    try:
        stanza.download('en', processors='tokenize,mwt,pos,constituency', verbose=False)
    except Exception as e:
        print(f"Error downloading Stanza models: {e}. Please ensure you have internet access or run 'stanza.download('en')' manually.")
        exit()

    # Test Case 1: Complex sentence with nested SBARs
    test_text_1 = "If it rains, and if the ground is wet, then we will cancel the picnic."
    print(f"\nAnalyzing Text 1: '{test_text_1}'")
    results_1 = measure_stanza_compound_assumptions(test_text_1)
    if results_1['success']:
        print("\nResults for Text 1:")
        print(f"  Nested SBAR Count: {results_1['nested_sbar_count']}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: Sentence with nested beliefs
    test_text_2 = "She believes that he thinks that the answer is correct."
    print(f"\nAnalyzing Text 2: '{test_text_2}'")
    results_2 = measure_stanza_compound_assumptions(test_text_2)
    if results_2['success']:
        print("\nResults for Text 2:")
        print(f"  Nested SBAR Count: {results_2['nested_sbar_count']}")
    else:
        print(f"  Error: {results_2['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Simple sentence
    test_text_3 = "The cat sat on the mat."
    print(f"\nAnalyzing Text 3: '{test_text_3}'")
    results_3 = measure_stanza_compound_assumptions(test_text_3)
    if results_3['success']:
        print("\nResults for Text 3:")
        print(f"  Nested SBAR Count: {results_3['nested_sbar_count']}")
    else:
        print(f"  Error: {results_3['error_message']}")
