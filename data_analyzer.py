import pandas as pd
import json
import os
import sys

# --- Global File Paths ---
BASE_DIR = r"C:\Users\ja\Documents\LLM_Eval"
JSONL_REPORT_FILEPATH = os.path.join(BASE_DIR, "query_analysis_report.jsonl")

# --- Function to Load and Flatten Data for Analysis ---
def load_and_flatten_for_analysis(filepath):
    """
    Loads the .jsonl report and flattens it into a Pandas DataFrame suitable for analysis.
    This version flattens original query dimensions and aggregates paraphrase metrics.
    """
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        if not records:
            print(f"Error: Input JSONL file '{filepath}' is empty or contains no valid JSON objects.", file=sys.stderr)
            return pd.DataFrame()
    except FileNotFoundError:
        print(f"Error: Input JSONL file not found at '{filepath}'. Please check the path.", file=sys.stderr)
        return pd.DataFrame()
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON found in '{filepath}'. Please check the file's content. Error: {e}", file=sys.stderr)
        return pd.DataFrame()
    except Exception as e:
        print(f"An unexpected error occurred while reading the JSONL file: {e}", file=sys.stderr)
        return pd.DataFrame()

    flattened_data = []
    for record in records:
        row_data = {
            'query_text': record.get('query_text', ''),
            'analysis_timestamp': record.get('analysis_timestamp', '')
        }
        
        # Flatten original_query_dimensions
        original_dims = record.get('original_query_dimensions', {})
        for dim_name, dim_values in original_dims.items():
            if isinstance(dim_values, dict):
                for k, v in dim_values.items():
                    # For analysis, we might keep lists as lists or join them
                    # For now, joining to string for simplicity in a flat table
                    row_data[f"original_query_dimensions_{dim_name}_{k}"] = "; ".join(map(str, v)) if isinstance(v, list) else v
            else:
                row_data[f"original_query_dimensions_{dim_name}"] = dim_values
        
        # Process paraphrases: Calculate aggregated metrics for paraphrases
        paraphrases_list = record.get('paraphrases', [])
        row_data['num_paraphrases'] = len(paraphrases_list)
        
        if paraphrases_list:
            # Collect paraphrase lengths and distances
            paraphrase_lengths = []
            paraphrase_word_distances = []
            paraphrase_char_distances = []
            
            for p_data in paraphrases_list:
                p_dims = p_data.get('paraphrase_dimensions', {})
                p_len_tokens = p_dims.get('length_and_tokens', {}).get('num_total_tokens')
                if p_len_tokens is not None:
                    paraphrase_lengths.append(p_len_tokens)
                
                p_dist = p_data.get('paraphrase_distance_to_original', {})
                word_dist = p_dist.get('word_level', {}).get('word_level_distance')
                char_dist = p_dist.get('char_level', {}).get('char_level_distance')
                
                if word_dist is not None and word_dist != -1: # Exclude -1 for failed calculations
                    paraphrase_word_distances.append(word_dist)
                if char_dist is not None and char_dist != -1: # Exclude -1 for failed calculations
                    paraphrase_char_distances.append(char_dist)
            
            # Add aggregated paraphrase metrics to the main row
            row_data['avg_paraphrase_length'] = sum(paraphrase_lengths) / len(paraphrase_lengths) if paraphrase_lengths else 0
            row_data['avg_paraphrase_word_distance'] = sum(paraphrase_word_distances) / len(paraphrase_word_distances) if paraphrase_word_distances else 0
            row_data['avg_paraphrase_char_distance'] = sum(paraphrase_char_distances) / len(paraphrase_char_distances) if paraphrase_char_distances else 0
            
            # Also store the raw paraphrase list for more detailed analysis if needed
            row_data['paraphrases_raw'] = paraphrases_list
        else:
            row_data['avg_paraphrase_length'] = 0
            row_data['avg_paraphrase_word_distance'] = 0
            row_data['avg_paraphrase_char_distance'] = 0
            row_data['paraphrases_raw'] = [] # Ensure it's an empty list if no paraphrases
            
        flattened_data.append(row_data)

    df = pd.DataFrame(flattened_data)
    return df

# --- Analytical Functions ---

def analyze_overall_query_metrics(df):
    """
    Calculates and prints overall average metrics for original queries.
    """
    print("\n--- Overall Original Query Metrics ---")
    if df.empty:
        print("No data to analyze.")
        return

    # Select key numeric columns for overall averages
    metrics_to_average = [
        'original_query_dimensions_length_and_tokens_num_total_tokens',
        'original_query_dimensions_semantic_complexity_stanza_parse_tree_depth',
        'original_query_dimensions_logical_markers_modality_marker_count',
        'original_query_dimensions_abstractness_concreteness_average_concreteness_score',
        'original_query_dimensions_ambiguity_spacy_pronoun_pronoun_count',
        'original_query_dimensions_compound_assumptions_spacy_nested_clauses_count',
        'original_query_dimensions_ambiguity_coreferee_total_coref_chains'
    ]
    
    # Ensure columns exist and are numeric before averaging
    available_metrics = [col for col in metrics_to_average if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    
    if not available_metrics:
        print("No numeric original query dimensions found for averaging.")
        return

    avg_metrics = df[available_metrics].mean().round(2)
    print("Average Metrics Across All Original Queries:")
    print(avg_metrics.to_string())
    print("-" * 40)

def analyze_paraphrase_relationships(df):
    """
    Analyzes relationships between original queries and their paraphrases.
    """
    print("\n--- Paraphrase Relationship Analysis ---")
    if df.empty:
        print("No data to analyze.")
        return

    # Filter for queries that actually have paraphrases
    df_with_paraphrases = df[df['num_paraphrases'] > 0].copy()

    if df_with_paraphrases.empty:
        print("No queries with paraphrases found for relationship analysis.")
        return

    print(f"Analyzing {len(df_with_paraphrases)} queries with paraphrases.")

    # Average difference in length between original query and its paraphrases
    # Ensure columns exist and are numeric
    if 'original_query_dimensions_length_and_tokens_num_total_tokens' in df_with_paraphrases.columns and \
       'avg_paraphrase_length' in df_with_paraphrases.columns:
        df_with_paraphrases['length_diff'] = df_with_paraphrases['avg_paraphrase_length'] - \
                                             df_with_paraphrases['original_query_dimensions_length_and_tokens_num_total_tokens']
        print(f"Average difference in total tokens (Paraphrase - Original): {df_with_paraphrases['length_diff'].mean():.2f}")
    else:
        print("Required length columns not found for difference analysis.")

    # Correlation between original query length and average paraphrase distance
    if 'original_query_dimensions_length_and_tokens_num_total_tokens' in df_with_paraphrases.columns and \
       'avg_paraphrase_word_distance' in df_with_paraphrases.columns:
        correlation = df_with_paraphrases['original_query_dimensions_length_and_tokens_num_total_tokens'].corr(
            df_with_paraphrases['avg_paraphrase_word_distance']
        )
        print(f"Correlation between Original Query Length and Average Paraphrase Word Distance: {correlation:.2f}")
    else:
        print("Required columns for correlation analysis not found.")
    
    print("-" * 40)

def find_extreme_queries(df, metric_column, top_n=3, ascending=False):
    """
    Finds queries with the highest/lowest values for a given metric.
    """
    print(f"\n--- Top {top_n} Queries by '{metric_column}' ({'Lowest' if ascending else 'Highest'}) ---")
    if df.empty or metric_column not in df.columns or not pd.api.types.is_numeric_dtype(df[metric_column]):
        print(f"Cannot find extreme queries for '{metric_column}'. Column not found or not numeric.")
        return

    extreme_queries = df.sort_values(by=metric_column, ascending=ascending).head(top_n)
    for index, row in extreme_queries.iterrows():
        print(f"Query: '{row['query_text'][:70]}...'")
        print(f"  {metric_column}: {row[metric_column]:.2f}")
        if 'num_paraphrases' in row and row['num_paraphrases'] > 0:
            print(f"  Number of Paraphrases: {row['num_paraphrases']}")
            if 'avg_paraphrase_word_distance' in row:
                print(f"  Avg Paraphrase Word Distance: {row['avg_paraphrase_word_distance']:.2f}")
        print("-" * 20)
    print("-" * 40)


if __name__ == "__main__":
    print("--- Running Query Analysis Data Analyzer ---")
    print("This script performs analytical queries on your structured JSONL report.")
    print("="*80)
    print(f"Loading data from: {JSONL_REPORT_FILEPATH}")
    print("="*80)

    # Load and flatten the data
    analysis_df = load_and_flatten_for_analysis(JSONL_REPORT_FILEPATH)

    if not analysis_df.empty:
        print(f"Successfully loaded and flattened {len(analysis_df)} unique queries.")
        print(f"DataFrame shape: {analysis_df.shape}")
        
        # Perform analyses
        analyze_overall_query_metrics(analysis_df)
        analyze_paraphrase_relationships(analysis_df)
        
        # Example: Find queries with highest parse tree depth
        find_extreme_queries(analysis_df, 'original_query_dimensions_semantic_complexity_stanza_parse_tree_depth', top_n=5, ascending=False)
        
        # Example: Find queries with lowest concreteness score (most abstract)
        find_extreme_queries(analysis_df, 'original_query_dimensions_abstractness_concreteness_average_concreteness_score', top_n=5, ascending=True)

        # Example: Find queries with highest average paraphrase word distance
        find_extreme_queries(analysis_df, 'avg_paraphrase_word_distance', top_n=5, ascending=False)

    else:
        print("No data loaded for analysis. Please check your JSONL file.")

    print("\n--- Analysis Complete ---")