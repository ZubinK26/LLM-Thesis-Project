import spacy
import coreferee
import sys # NEW: Import sys for stderr

# Initialize the spaCy NLP pipeline with Coreferee once globally.
_spacy_nlp_coreferee = None

def _initialize_spacy_nlp_coreferee():
    """Initializes and returns the spaCy NLP pipeline with Coreferee."""
    global _spacy_nlp_coreferee
    if _spacy_nlp_coreferee is None:
        try:
            # MODIFIED: Redirect print statements to sys.stderr
            print("Initializing spaCy NLP pipeline with Coreferee...", file=sys.stderr)
            nlp = spacy.load("en_core_web_lg")  # large model recommended
            nlp.add_pipe("coreferee")
            _spacy_nlp_coreferee = nlp
            print("spaCy NLP pipeline with Coreferee initialized successfully.", file=sys.stderr)
        except OSError:
            print("Error: spaCy model 'en_core_web_lg' not found. Please run:", file=sys.stderr)
            print("    python -m spacy download en_core_web_lg", file=sys.stderr)
            _spacy_nlp_coreferee = None
        except Exception as e:
            print(f"An unexpected error occurred while loading spaCy with Coreferee: {e}", file=sys.stderr)
            _spacy_nlp_coreferee = None
    return _spacy_nlp_coreferee

def measure_coreferee_unresolved_references(text):
    """
    Detects coreference chains and identifies pronouns within them.
    Returns counts and a description of each chain.
    """
    results = {
        'total_coref_chains': 0,
        'pronouns_in_chains_count': 0,
        'coreference_chains_info': [],
        'success': False,
        'error_message': None
    }

    nlp = _initialize_spacy_nlp_coreferee()
    if nlp is None:
        results['error_message'] = "spaCy NLP pipeline with Coreferee failed to initialize."
        return results

    try:
        doc = nlp(text)
        chains_info = []
        pronouns_in_chains = set()

        if doc._.coref_chains:
            results['total_coref_chains'] = len(doc._.coref_chains)
            for chain_id, chain_obj in enumerate(doc._.coref_chains):
                mention_texts = []
                # chain_obj is iterable of Mention objects (token index or list of indices)
                for mention in chain_obj:
                    # Reconstruct the actual tokens for each mention
                    if isinstance(mention, int):
                        span_tokens = [doc[mention]]
                    else:
                        span_tokens = [doc[i] for i in mention]
                    # Join tokens to form the mention string
                    mention_str = " ".join(tok.text for tok in span_tokens)
                    mention_texts.append(mention_str)
                    # Collect pronouns in those tokens
                    for tok in span_tokens:
                        if tok.pos_ == "PRON":
                            pronouns_in_chains.add(tok.text.lower())

                chains_info.append(f"Chain {chain_id}: {mention_texts}")

        results['coreference_chains_info'] = chains_info
        results['pronouns_in_chains_count'] = len(pronouns_in_chains)
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during Coreferee processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    # MODIFIED: Redirect print statements in standalone test block to sys.stderr
    print("--- Running Ambiguity (Coreferee Unresolved References) Test (Standalone) ---", file=sys.stderr)

    test_texts = [
        "Alice went to the park. She saw Bob there. He was reading a book.",
        "The engineers built a new bridge. They were very proud of their work. It stood strong.",
        "The old man spoke to the young boy. He seemed tired."
    ]
    for i, text in enumerate(test_texts, start=1):
        print(f"\nAnalyzing Text {i}: '{text}'", file=sys.stderr)
        results = measure_coreferee_unresolved_references(text)
        if results['success']:
            print(f"  Total Coreference Chains: {results['total_coref_chains']}", file=sys.stderr)
            print(f"  Pronouns in Chains: {results['pronouns_in_chains_count']}", file=sys.stderr)
            print("  Chains Detail:", file=sys.stderr)
            for chain in results['coreference_chains_info']:
                print(f"    - {chain}", file=sys.stderr)
        else:
            print(f"  Error: {results['error_message']}", file=sys.stderr)


