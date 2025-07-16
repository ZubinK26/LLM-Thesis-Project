import sys
import json
from datetime import datetime

# Import the Coreferee dimension measurement function
# IMPORTANT: Ensure coref_test.py is in the same directory as this script.
from coref_test import measure_coreferee_unresolved_references

def run_coreferee_analysis(query_text):
    """
    Runs the Coreferee dimension analysis on a given query.

    Args:
        query_text (str): The query text to analyze.

    Returns:
        dict: A dictionary containing Coreferee analysis results.
    """
    # MODIFIED: Redirect verbose messages to stderr
    print(f"\n--- Starting Coreferee Analysis for Query: '{query_text[:70]}...' ---", file=sys.stderr)
    coreferee_results = measure_coreferee_unresolved_references(query_text)
    print("--- Coreferee Analysis Completed ---", file=sys.stderr)
    return coreferee_results

if __name__ == "__main__":
    # This script expects the query text as a command-line argument.
    if len(sys.argv) < 2:
        print("Usage: python coreferee_reporter.py \"Your query text here\"", file=sys.stderr)
        # For standalone testing, provide a default query
        query_to_analyze = "Alice went to the park. She saw Bob there. He was reading a book."
        print(f"No query provided as argument. Using default test query: '{query_to_analyze}'", file=sys.stderr)
    else:
        query_to_analyze = sys.argv[1]

    results = run_coreferee_analysis(query_to_analyze)
    
    # Print the results as a JSON string to standard output.
    # The main master script will capture this output.
    print(json.dumps(results))