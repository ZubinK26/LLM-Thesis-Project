import stanza

# Initialize the Stanza pipeline once globally or pass it to the function
# This helps avoid re-initializing the pipeline for every call if used in a loop.
# It's recommended to initialize outside the function if the function is called many times.
# For standalone testing within this script, initializing inside is fine.
_stanza_nlp_pipeline = None

def _initialize_stanza_nlp():
    """Initializes and returns the Stanza NLP pipeline."""
    global _stanza_nlp_pipeline
    if _stanza_nlp_pipeline is None:
        try:
            print("Initializing Stanza NLP pipeline...")
            _stanza_nlp_pipeline = stanza.Pipeline(
                lang='en',
                processors='tokenize,mwt,pos,constituency',
                use_gpu=False, # Set to True if you have a compatible GPU and drivers
                verbose=False # Suppress verbose loading messages for cleaner output
            )
            print("Stanza NLP pipeline initialized successfully.")
        except Exception as e:
            print(f"Error initializing Stanza NLP pipeline: {e}")
            _stanza_nlp_pipeline = None # Ensure it's None if initialization fails
    return _stanza_nlp_pipeline

def get_parse_tree_depth(node):
    """Recursively calculates the maximum depth of a constituency parse tree node."""
    if not node.children:
        return 1
    return 1 + max(get_parse_tree_depth(child) for child in node.children)

def count_subordinate_clauses(node):
    """Recursively counts SBAR (subordinate clause) nodes in a constituency parse tree."""
    count = 1 if node.label == "SBAR" else 0
    for child in node.children:
        count += count_subordinate_clauses(child)
    return count

def measure_stanza_semantic_complexity(text):
    """
    Measures parse-tree depth and subordinate clause count using Stanza's constituency parser.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'parse_tree_depth': Integer depth of the constituency parse tree.
              - 'subordinate_clause_count': Integer count of SBAR (subordinate clause) nodes.
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'parse_tree_depth': 0,
        'subordinate_clause_count': 0,
        'success': False,
        'error_message': None
    }

    nlp = _initialize_stanza_nlp()
    if nlp is None:
        results['error_message'] = "Stanza NLP pipeline failed to initialize."
        return results

    try:
        doc = nlp(text)
        if not doc.sentences:
            results['error_message'] = "No sentences detected in the text by Stanza."
            return results

        # Assuming we analyze the first sentence for simplicity, as per previous examples.
        # For multi-sentence queries, you might want to average or sum these metrics.
        tree = doc.sentences[0].constituency

        results['parse_tree_depth'] = get_parse_tree_depth(tree)
        results['subordinate_clause_count'] = count_subordinate_clauses(tree)
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during Stanza text processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Semantic Complexity (Stanza) Dimension Test (Standalone) ---")

    # Ensure Stanza models are downloaded if not already present
    # This part is for standalone script execution. In a master script,
    # you'd ideally handle Stanza model downloads once.
    try:
        stanza.download('en', processors='tokenize,mwt,pos,constituency', verbose=False)
    except Exception as e:
        print(f"Error downloading Stanza models: {e}. Please ensure you have internet access or run 'stanza.download('en')' manually.")
        # Exit or handle gracefully if models cannot be downloaded for standalone test
        exit()

    # Test Case 1: Complex sentence with nested SBARs
    test_text_1 = "If it rains, and if the ground is wet, then we will cancel the picnic."
    print(f"\nAnalyzing Text 1: '{test_text_1}'")
    results_1 = measure_stanza_semantic_complexity(test_text_1)
    if results_1['success']:
        print("\nResults for Text 1:")
        print(f"  Parse-tree depth: {results_1['parse_tree_depth']}")
        print(f"  Subordinate-clause count (SBAR): {results_1['subordinate_clause_count']}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: Sentence with nested beliefs
    test_text_2 = "She believes that he thinks that the answer is correct."
    print(f"\nAnalyzing Text 2: '{test_text_2}'")
    results_2 = measure_stanza_semantic_complexity(test_text_2)
    if results_2['success']:
        print("\nResults for Text 2:")
        print(f"  Parse-tree depth: {results_2['parse_tree_depth']}")
        print(f"  Subordinate-clause count (SBAR): {results_2['subordinate_clause_count']}")
    else:
        print(f"  Error: {results_2['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Simple sentence
    test_text_3 = "The cat sat on the mat."
    print(f"\nAnalyzing Text 3: '{test_text_3}'")
    results_3 = measure_stanza_semantic_complexity(test_text_3)
    if results_3['success']:
        print("\nResults for Text 3:")
        print(f"  Parse-tree depth: {results_3['parse_tree_depth']}")
        print(f"  Subordinate-clause count (SBAR): {results_3['subordinate_clause_count']}")
    else:
        print(f"  Error: {results_3['error_message']}")