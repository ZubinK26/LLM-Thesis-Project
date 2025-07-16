import spacy

def check_spacy_lg_model():
    """
    Checks if the 'en_core_web_lg' spaCy model is installed and loadable.
    """
    try:
        print("Attempting to load 'en_core_web_lg' spaCy model...")
        nlp = spacy.load("en_core_web_lg")
        print(f"SUCCESS: spaCy model '{nlp.meta['name']}' loaded successfully.")
        print("You are ready to use functions that require this model.")
        return True
    except OSError:
        print("ERROR: spaCy model 'en_core_web_lg' not found.")
        print("Please install it by running: python -m spacy download en_core_web_lg")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

if __name__ == "__main__":
    check_spacy_lg_model()