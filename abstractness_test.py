import spacy
import pandas as pd
import os

# Initialize the spaCy NLP pipeline once globally.
_spacy_nlp_concreteness = None

def _initialize_spacy_nlp_concreteness():
    """Initializes and returns the spaCy NLP pipeline for concreteness analysis."""
    global _spacy_nlp_concreteness
    if _spacy_nlp_concreteness is None:
        try:
            print("Initializing spaCy NLP pipeline for concreteness...")
            _spacy_nlp_concreteness = spacy.load("en_core_web_md")
            print("spaCy NLP pipeline for concreteness initialized successfully.")
        except OSError:
            print("Error: spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md")
            _spacy_nlp_concreteness = None
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy for concreteness: {e}")
            _spacy_nlp_concreteness = None
    return _spacy_nlp_concreteness

# Global variable to store the loaded concreteness lexicon for efficiency
_concreteness_lexicon = None
_concreteness_lexicon_filepath_cached = None

def _load_concreteness_lexicon(concreteness_filepath):
    """Loads and caches the Brysbaert Concreteness Ratings lexicon."""
    global _concreteness_lexicon, _concreteness_lexicon_filepath_cached

    # Only load if not already loaded or if the filepath has changed
    if _concreteness_lexicon is None or _concreteness_lexicon_filepath_cached != concreteness_filepath:
        _concreteness_lexicon = {} # Reset
        _concreteness_lexicon_filepath_cached = None # Reset
        try:
            if not os.path.exists(concreteness_filepath):
                return None, f"Concreteness CSV file not found at '{concreteness_filepath}'. Please ensure the path is correct."

            df = pd.read_csv(concreteness_filepath, encoding='utf-8')
            # Assuming the word column is named 'Word' and the score column is 'Conc.M'
            _concreteness_lexicon = dict(zip(df['Word'].str.lower(), df['Conc.M']))
            _concreteness_lexicon_filepath_cached = concreteness_filepath
            # print(f"Successfully loaded {len(_concreteness_lexicon)} concreteness ratings from CSV.") # Optional: for debugging setup
            return _concreteness_lexicon, None

        except KeyError:
            return None, "Expected 'Word' or 'Conc.M' column not found in the CSV. Please check your CSV file's column headers."
        except Exception as e:
            return None, f"An unexpected error occurred while loading the CSV: {e}"
    
    return _concreteness_lexicon, None # Return cached lexicon if already loaded

def measure_concreteness_score(text, concreteness_filepath):
    """
    Tests the abstractness/concreteness of a text using Brysbaert Concreteness Ratings.
    Calculates an average concreteness score for the input text.

    Args:
        text (str): The input text to analyze.
        concreteness_filepath (str): The full path to the Brysbaert Concreteness Ratings CSV file.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'average_concreteness_score': Float, average score (1.0-5.0).
              - 'concreteness_classification': String (e.g., 'Highly Concrete', 'Moderately Abstract').
              - 'words_found_in_lexicon_count': Integer count of words from text found in lexicon.
              - 'individual_word_scores': List of strings, e.g., "'dog' (Lemma: dog, Score: 4.85)".
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'average_concreteness_score': 0.0,
        'concreteness_classification': 'N/A',
        'words_found_in_lexicon_count': 0,
        'individual_word_scores': [],
        'success': False,
        'error_message': None
    }

    nlp = _initialize_spacy_nlp_concreteness()
    if nlp is None:
        results['error_message'] = "spaCy NLP pipeline failed to initialize for concreteness."
        return results

    concreteness_lexicon, lexicon_error = _load_concreteness_lexicon(concreteness_filepath)
    if lexicon_error:
        results['error_message'] = lexicon_error
        return results
    if not concreteness_lexicon: # Lexicon might be empty but loaded successfully
        results['error_message'] = "Concreteness lexicon loaded successfully but is empty. Please check the CSV content."
        return results

    try:
        doc = nlp(text)

        total_score = 0
        word_count_with_scores = 0

        for token in doc:
            # We use lemma for better matching against the lexicon (e.g., "running" -> "run")
            lemma_lower = token.lemma_.lower()
            
            if lemma_lower in concreteness_lexicon:
                score = concreteness_lexicon[lemma_lower]
                results['individual_word_scores'].append(f"'{token.text}' (Lemma: {token.lemma_}, Score: {score:.2f})")
                total_score += score
                word_count_with_scores += 1
        
        results['words_found_in_lexicon_count'] = word_count_with_scores

        if word_count_with_scores > 0:
            average_concreteness = total_score / word_count_with_scores
            results['average_concreteness_score'] = round(average_concreteness, 2) # Round for cleaner output
            
            # Simple classification based on typical Brysbaert scale (1=abstract, 5=concrete)
            if average_concreteness >= 4.0:
                results['concreteness_classification'] = "Highly Concrete"
            elif average_concreteness >= 3.0:
                results['concreteness_classification'] = "Moderately Concrete"
            elif average_concreteness >= 2.0:
                results['concreteness_classification'] = "Moderately Abstract"
            else:
                results['concreteness_classification'] = "Highly Abstract"
            
            results['success'] = True
        else:
            results['error_message'] = "No words from the text were found in the concreteness lexicon."
            results['success'] = False # Indicate failure if no relevant words are found

    except Exception as e:
        results['error_message'] = f"An error occurred during concreteness score processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Abstractness vs. Concreteness Dimension Test (Standalone) ---")

    # IMPORTANT: Update this path to your actual CSV file location
    CONCRETENESS_CSV_PATH = r"C:\Users\ja\Documents\LLM_Eval\concreteness_scores_original.csv"

    # Test Case 1: More Concrete Text
    concrete_text = "The dog barked loudly at the red ball in the green park."
    print(f"\nAnalyzing Text 1: '{concrete_text}'")
    results_1 = measure_concreteness_score(concrete_text, CONCRETENESS_CSV_PATH)
    if results_1['success']:
        print("\nResults for Text 1:")
        print(f"  Average Concreteness Score: {results_1['average_concreteness_score']:.2f}")
        print(f"  Classification: {results_1['concreteness_classification']}")
        print(f"  Words Found in Lexicon: {results_1['words_found_in_lexicon_count']}")
        print("  Individual Word Scores:")
        for item in results_1['individual_word_scores']:
            print(f"    - {item}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 2: More Abstract Text
    abstract_text = "Truth, justice, and the pursuit of happiness are complex philosophical concepts."
    print(f"\nAnalyzing Text 2: '{abstract_text}'")
    results_2 = measure_concreteness_score(abstract_text, CONCRETENESS_CSV_PATH)
    if results_2['success']:
        print("\nResults for Text 2:")
        print(f"  Average Concreteness Score: {results_2['average_concreteness_score']:.2f}")
        print(f"  Classification: {results_2['concreteness_classification']}")
        print(f"  Words Found in Lexicon: {results_2['words_found_in_lexicon_count']}")
        print("  Individual Word Scores:")
        for item in results_2['individual_word_scores']:
            print(f"    - {item}")
    else:
        print(f"  Error: {results_2['error_message']}")

    print("\n" + "="*70 + "\n")

    # Test Case 3: Text with words likely not in lexicon (e.g., proper nouns, very specific terms)
    uncommon_text = "Quantum entanglement postulates instantaneous communication."
    print(f"\nAnalyzing Text 3: '{uncommon_text}'")
    results_3 = measure_concreteness_score(uncommon_text, CONCRETENESS_CSV_PATH)
    if results_3['success']:
        print("\nResults for Text 3:")
        print(f"  Average Concreteness Score: {results_3['average_concreteness_score']:.2f}")
        print(f"  Classification: {results_3['concreteness_classification']}")
        print(f"  Words Found in Lexicon: {results_3['words_found_in_lexicon_count']}")
        print("  Individual Word Scores:")
        for item in results_3['individual_word_scores']:
            print(f"    - {item}")
    else:
        print(f"  Error: {results_3['error_message']}")