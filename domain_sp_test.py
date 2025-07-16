import spacy
import os
from spacy.matcher import PhraseMatcher

# Initialize the spaCy NLP pipeline once globally.
_spacy_nlp_domain_terms = None

def _initialize_spacy_nlp_domain_terms():
    """Initializes and returns the spaCy NLP pipeline for domain term detection."""
    global _spacy_nlp_domain_terms
    if _spacy_nlp_domain_terms is None:
        try:
            print("Initializing spaCy NLP pipeline for domain terms...")
            _spacy_nlp_domain_terms = spacy.load("en_core_web_md")
            print("spaCy NLP pipeline for domain terms initialized successfully.")
        except OSError:
            print("Error: spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md")
            _spacy_nlp_domain_terms = None
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy for domain terms: {e}")
            _spacy_nlp_domain_terms = None
    return _spacy_nlp_domain_terms


def measure_domain_specific_terms(query_text, domain_terms_filepath):
    """
    Assesses a query to identify and count domain-specific terms (single words and phrases)
    from a given lexicon file.

    Args:
        query_text (str): The input query string to analyze.
        domain_terms_filepath (str): The full path to the .txt file containing domain-specific terms,
                                     one term per line. Multi-word terms should be on a single line.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'unique_domain_terms_count': Integer count of unique domain-specific terms found.
              - 'detected_terms': List of strings, e.g., "'function' (Lemma: function)" or "'approaches zero' (Phrase)".
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'unique_domain_terms_count': 0,
        'detected_terms': [],
        'success': False,
        'error_message': None
    }

    nlp = _initialize_spacy_nlp_domain_terms()
    if nlp is None:
        results['error_message'] = "spaCy NLP pipeline failed to initialize for domain terms."
        return results

    # 2. Load Domain Terms Lexicon from the specified file
    single_word_terms = set()
    multi_word_patterns = [] # For PhraseMatcher
    
    try:
        if not os.path.exists(domain_terms_filepath):
            results['error_message'] = f"Domain terms file not found at '{domain_terms_filepath}'. Please ensure the path is correct and the file exists."
            return results

        with open(domain_terms_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                term = line.strip().lower() # Normalize: remove whitespace, convert to lowercase
                if term: # Only add non-empty lines
                    if ' ' in term: # If term contains space, it's a multi-word phrase
                        multi_word_patterns.append(nlp.make_doc(term))
                    else: # Otherwise, it's a single word
                        single_word_terms.add(term)
        
        if not single_word_terms and not multi_word_patterns:
            results['error_message'] = f"The domain terms file '{domain_terms_filepath}' is empty or contains no valid terms. Please add terms to the file (one per line)."
            # We still proceed to analyze the query, but no terms will be found, and this warning will be captured.
            
    except Exception as e:
        results['error_message'] = f"An unexpected error occurred while loading the domain terms file: {e}"
        return results

    # Initialize PhraseMatcher for multi-word terms
    matcher = PhraseMatcher(nlp.vocab)
    if multi_word_patterns:
        matcher.add("DOMAIN_PHRASES", multi_word_patterns)

    # 3. Process the query text using spaCy
    try:
        doc = nlp(query_text)

        # Use a set to track unique matches (based on their normalized form) to prevent overcounting
        unique_matches_in_query = set() 

        # 4. Match single-word terms (using lemma for robustness)
        for token in doc:
            token_lower = token.text.lower()
            lemma_lower = token.lemma_.lower()
            
            # Check if the lowercased token text or its lowercased lemma is in our single_word_terms set
            if token_lower in single_word_terms or lemma_lower in single_word_terms:
                # Use the lemma_lower as the key for uniqueness to count "function" and "functions" as one match
                if lemma_lower not in unique_matches_in_query:
                    results['detected_terms'].append(f"'{token.text}' (Lemma: {token.lemma_})")
                    unique_matches_in_query.add(lemma_lower)
        
        # 5. Match multi-word phrases using PhraseMatcher
        matches = matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end] # The matched span of tokens
            phrase_text = span.text.lower() # The matched phrase
            
            # Add the full phrase to found_terms if not already added (using the phrase text for uniqueness)
            if phrase_text not in unique_matches_in_query:
                results['detected_terms'].append(f"'{span.text}' (Phrase)")
                unique_matches_in_query.add(phrase_text) # Use the full phrase for uniqueness

        results['unique_domain_terms_count'] = len(results['detected_terms'])
        results['detected_terms'].sort() # Sort for consistent output
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during domain term detection processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Domain-Specific Terms Test (Standalone) ---")

    # IMPORTANT: Set this path to your actual .txt file location
    DOMAIN_TERMS_FILEPATH = r"C:\Users\ja\Documents\LLM_Eval\domain_sp_words.txt"

    # --- Instructions for creating and populating domain_sp_words.txt ---
    # These instructions are kept minimal here, as per our last discussion.
    # More detailed instructions for populating the file will be provided outside the code block.
    print(f"\nEnsure your 'domain_sp_words.txt' file exists at: {DOMAIN_TERMS_FILEPATH}")
    print("It should contain one domain term or phrase per line (e.g., 'limit', 'vector space').")
    print("="*70)

    # Test Case 1: Query with single words and a multi-word phrase
    query_1 = "What is the limit of a function as its derivative approaches zero in a vector space?"
    print(f"\nAnalyzing Query 1: '{query_1}'")
    results_1 = measure_domain_specific_terms(query_1, DOMAIN_TERMS_FILEPATH)
    if results_1['success']:
        print("\nResults for Query 1:")
        print(f"  Unique Domain Terms Count: {results_1['unique_domain_terms_count']}")
        print(f"  Detected Terms: {results_1['detected_terms']}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: Query with no expected domain terms
    query_2 = "The quick brown fox jumps over the lazy dog."
    print(f"\nAnalyzing Query 2: '{query_2}'")
    results_2 = measure_domain_specific_terms(query_2, DOMAIN_TERMS_FILEPATH)
    if results_2['success']:
        print("\nResults for Query 2:")
        print(f"  Unique Domain Terms Count: {results_2['unique_domain_terms_count']}")
        print(f"  Detected Terms: {results_2['detected_terms']}")
    else:
        print(f"  Error: {results_2['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Query with variations (e.g., plural forms) and another phrase
    query_3 = "Are there different types of matrices or functions? We are given that this is a compact set."
    print(f"\nAnalyzing Query 3: '{query_3}'")
    results_3 = measure_domain_specific_terms(query_3, DOMAIN_TERMS_FILEPATH)
    if results_3['success']:
        print("\nResults for Query 3:")
        print(f"  Unique Domain Terms Count: {results_3['unique_domain_terms_count']}")
        print(f"  Detected Terms: {results_3['detected_terms']}")
    else:
        print(f"  Error: {results_3['error_message']}")