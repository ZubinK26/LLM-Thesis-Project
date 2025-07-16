import spacy

def measure_length_and_tokens(text):
    """
    Measures the number of sentences, total tokens, and word tokens in a given text.

    Args:
        text (str): The input text to analyze.

    Returns:
        dict: A dictionary containing the following metrics:
              - 'num_sentences': Integer count of sentences.
              - 'num_total_tokens': Integer count of all spaCy tokens (words, punctuation, spaces).
              - 'num_word_tokens': Integer count of only alphabetic word tokens.
              - 'sentences': List of sentence texts.
              - 'word_tokens_list': List of alphabetic word tokens.
              - 'success': Boolean indicating if the operation was successful.
              - 'error_message': String with error details if any.
    """
    results = {
        'num_sentences': 0,
        'num_total_tokens': 0,
        'num_word_tokens': 0,
        'sentences': [],
        'word_tokens_list': [],
        'success': False,
        'error_message': None
    }

    try:
        # Load the en_core_web_md model (user confirmed they have 'md', not 'sm')
        nlp = spacy.load("en_core_web_md")
        # print(f"Successfully loaded spaCy model: {nlp.meta['name']}") # Optional: for debugging setup
    except OSError:
        results['error_message'] = "spaCy model 'en_core_web_md' not found. Please run: python -m spacy download en_core_web_md"
        return results
    except Exception as e:
        results['error_message'] = f"An unexpected error occurred while loading spaCy: {e}"
        return results

    try:
        doc = nlp(text)

        # Counting Sentences
        sentences = [sent.text for sent in doc.sents]
        results['num_sentences'] = len(sentences)
        results['sentences'] = sentences

        # Counting Total Tokens (including punctuation and spaces)
        results['num_total_tokens'] = len(doc)

        # Counting only Word Tokens (excluding punctuation and spaces)
        word_tokens = [token.text for token in doc if token.is_alpha]
        results['num_word_tokens'] = len(word_tokens)
        results['word_tokens_list'] = word_tokens
        
        results['success'] = True

    except Exception as e:
        results['error_message'] = f"An error occurred during text processing: {e}"
        results['success'] = False

    return results

if __name__ == "__main__":
    print("--- Running Length and Tokens Dimension Test (Standalone) ---")

    test_text_1 = """This is the first sentence. Here is the second sentence, which is a bit longer.
And finally, a third sentence. Let's count them!"""
    
    test_text_2 = "A single, short sentence."

    print(f"\nAnalyzing Text 1:\n'{test_text_1}'")
    results_1 = measure_length_and_tokens(test_text_1)
    if results_1['success']:
        print("\nResults for Text 1:")
        print(f"  Number of Sentences: {results_1['num_sentences']}")
        print(f"  Number of Total Tokens: {results_1['num_total_tokens']}")
        print(f"  Number of Word Tokens: {results_1['num_word_tokens']}")
        print("  Sentences:")
        for i, sent in enumerate(results_1['sentences']):
            print(f"    {i+1}: {sent}")
        print("  Word Tokens:")
        for word in results_1['word_tokens_list']:
            print(f"    - {word}")
    else:
        print(f"  Error: {results_1['error_message']}")

    print("\n" + "="*70 + "\n")

    print(f"\nAnalyzing Text 2:\n'{test_text_2}'")
    results_2 = measure_length_and_tokens(test_text_2)
    if results_2['success']:
        print("\nResults for Text 2:")
        print(f"  Number of Sentences: {results_2['num_sentences']}")
        print(f"  Number of Total Tokens: {results_2['num_total_tokens']}")
        print(f"  Number of Word Tokens: {results_2['num_word_tokens']}")
        print("  Sentences:")
        for i, sent in enumerate(results_2['sentences']):
            print(f"    {i+1}: {sent}")
        print("  Word Tokens:")
        for word in results_2['word_tokens_list']:
            print(f"    - {word}")
    else:
        print(f"  Error: {results_2['error_message']}")