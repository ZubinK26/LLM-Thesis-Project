import re

def evaluate_hedging_count(unconstrained_llm_response: str) -> dict:
    """
    Measures the number of hedging phrases used in the unconstrained LLM response.
    Hedging phrases indicate uncertainty or caution in the language.

    Args:
        unconstrained_llm_response (str): The full unconstrained response from the LLM.

    Returns:
        dict: A dictionary containing the hedging phrase count, success status, and error message.
    """
    try:
        if not isinstance(unconstrained_llm_response, str) or not unconstrained_llm_response.strip():
            return {
                'hedging_count': 0,
                'success': True,
                'error_message': "Empty or invalid unconstrained LLM response."
            }

        # Define a list of common hedging phrases and words.
        # These are case-insensitive and will be matched as whole words or phrases.
        # Using regex for more flexible matching (e.g., word boundaries).
        hedging_phrases = [
            r'\b(?:it seems)\b',
            r'\b(?:it appears)\b',
            r'\b(?:may be)\b',
            r'\b(?:might be)\b',
            r'\b(?:could be)\b',
            r'\b(?:suggests that)\b',
            r'\b(?:potentially)\b',
            r'\b(?:I believe)\b',
            r'\b(?:in my opinion)\b',
            r'\b(?:often)\b',
            r'\b(?:typically)\b',
            r'\b(?:generally)\b',
            r'\b(?:some argue)\b',
            r'\b(?:it is possible)\b',
            r'\b(?:it is likely)\b',
            r'\b(?:appears to be)\b',
            r'\b(?:can be seen as)\b',
            r'\b(?:tends to)\b',
            r'\b(?:seems to)\b',
            r'\b(?:possibly)\b',
            r'\b(?:presumably)\b',
            r'\b(?:in some cases)\b',
            r'\b(?:from my understanding)\b'
        ]

        count = 0
        # Convert response to lowercase once for case-insensitive matching
        lower_response = unconstrained_llm_response.lower()

        for phrase in hedging_phrases:
            # Use re.findall to count all non-overlapping occurrences
            count += len(re.findall(phrase, lower_response))

        return {
            'hedging_count': count,
            'success': True,
            'error_message': None
        }

    except Exception as e:
        return {
            'hedging_count': 0,
            'success': False,
            'error_message': f"Error evaluating hedging count: {e}"
        }

# Example Usage (for testing purposes, not part of the main script)
if __name__ == '__main__':
    response1 = "It seems that the answer might be correct, possibly. I believe this is generally true in some cases."
    response2 = "The capital of France is Paris. This statement is definitively true."
    response3 = ""
    response4 = "It appears to be a complex issue, and it is possible that there are other factors involved."

    print(f"Response 1: '{response1}'")
    print(f"Hedging Count: {evaluate_hedging_count(response1)}")
    print("-" * 30)

    print(f"Response 2: '{response2}'")
    print(f"Hedging Count: {evaluate_hedging_count(response2)}")
    print("-" * 30)

    print(f"Response 3: '{response3}'")
    print(f"Hedging Count: {evaluate_hedging_count(response3)}")
    print("-" * 30)

    print(f"Response 4: '{response4}'")
    print(f"Hedging Count: {evaluate_hedging_count(response4)}")
    print("-" * 30)