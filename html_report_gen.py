import pandas as pd
import json
import os
import sys

# --- Global File Paths ---
BASE_DIR = r"C:\Users\ja\Documents\LLM_Eval"
JSONL_REPORT_FILEPATH = os.path.join(BASE_DIR, "query_analysis_report.jsonl")
HTML_REPORT_FILEPATH = os.path.join(BASE_DIR, "query_analysis_report.html")

# --- Helper function to format paraphrase details into HTML ---
def format_paraphrases_to_html(paraphrases_list):
    """
    Converts a list of paraphrase dictionaries into a structured HTML unordered list.
    """
    if not paraphrases_list:
        return "<em>No paraphrases provided.</em>"

    html_output = "<ul>"
    for p_data in paraphrases_list:
        p_text = p_data.get('paraphrase_text', 'N/A')
        
        # Extract key dimensions for display
        p_dims = p_data.get('paraphrase_dimensions', {})
        p_len_tokens = p_dims.get('length_and_tokens', {}).get('num_total_tokens', 'N/A')
        p_avg_concreteness = p_dims.get('abstractness_concreteness', {}).get('average_concreteness_score', 'N/A')
        
        # Extract paraphrase distance
        p_dist = p_data.get('paraphrase_distance_to_original', {})
        word_dist = p_dist.get('word_level', {}).get('word_level_distance', 'N/A')
        char_dist = p_dist.get('char_level', {}).get('char_level_distance', 'N/A')

        html_output += f"""
        <li>
            <strong>Paraphrase:</strong> {p_text}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;<strong>Length (tokens):</strong> {p_len_tokens}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;<strong>Avg Concreteness:</strong> {p_avg_concreteness:.2f} (if numeric)<br>
            &nbsp;&nbsp;&nbsp;&nbsp;<strong>Word Distance to Original:</strong> {word_dist}<br>
            &nbsp;&nbsp;&nbsp;&nbsp;<strong>Char Distance to Original:</strong> {char_dist}
        </li>
        """
    html_output += "</ul>"
    return html_output

# --- Main function to load, process, and generate HTML ---
def generate_html_report(jsonl_filepath, html_output_filepath):
    """
    Loads data from a .jsonl file, processes it into a flat DataFrame
    with HTML-formatted paraphrase details, and generates an HTML report.
    """
    records = []
    try:
        with open(jsonl_filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))
        if not records:
            print(f"Error: Input JSONL file '{jsonl_filepath}' is empty or contains no valid JSON objects.", file=sys.stderr)
            return
    except FileNotFoundError:
        print(f"Error: Input JSONL file not found at '{jsonl_filepath}'. Please check the path.", file=sys.stderr)
        return
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON found in '{jsonl_filepath}'. Please check the file's content. Error: {e}", file=sys.stderr)
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the JSONL file: {e}", file=sys.stderr)
        return

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
                    # Join lists into strings for display in DataFrame
                    row_data[f"original_query_dimensions_{dim_name}_{k}"] = "; ".join(map(str, v)) if isinstance(v, list) else v
            else:
                row_data[f"original_query_dimensions_{dim_name}"] = dim_values
        
        # Process and format paraphrases into HTML for a single cell
        paraphrases_list = record.get('paraphrases', [])
        row_data['paraphrases_details'] = format_paraphrases_to_html(paraphrases_list)
        row_data['num_paraphrases'] = len(paraphrases_list)
        
        flattened_data.append(row_data)

    df = pd.DataFrame(flattened_data)
    
    # Reorder columns for better readability
    cols = ['query_text', 'analysis_timestamp', 'num_paraphrases', 'paraphrases_details'] + \
           [col for col in df.columns if col not in ['query_text', 'analysis_timestamp', 'num_paraphrases', 'paraphrases_details']]
    df = df[cols]

    # Convert DataFrame to HTML
    html_table = df.to_html(escape=False, index=False) # escape=False is crucial for rendering HTML in cells

    # Add basic HTML structure and styling
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Query Analysis Report</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; margin: 20px; background-color: #f4f7f6; color: #333; }}
        h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
        table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); border-radius: 8px; overflow: hidden; }}
        th, td {{ border: 1px solid #ddd; padding: 12px 15px; text-align: left; vertical-align: top; }}
        th {{ background-color: #e0f2f7; color: #2c3e50; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        tr:hover {{ background-color: #f1f1f1; }}
        ul {{ list-style-type: none; padding: 0; margin: 0; }}
        li {{ margin-bottom: 10px; padding-left: 10px; border-left: 2px solid #a7d9ed; }}
        li:last-child {{ margin-bottom: 0; }}
        em {{ color: #777; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; background-color: #fff; border-radius: 10px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Query Linguistic Analysis Report</h1>
        {html_table}
    </div>
</body>
</html>
    """

    try:
        with open(html_output_filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"\nSuccessfully generated HTML report: '{html_output_filepath}'")
    except Exception as e:
        print(f"Error writing HTML report to '{html_output_filepath}': {e}", file=sys.stderr)


if __name__ == "__main__":
    print("--- Running HTML Report Generator ---")
    print("This script converts your .jsonl analysis report into a browsable HTML file.")
    print("="*80)
    print(f"Input JSONL: {JSONL_REPORT_FILEPATH}")
    print(f"Output HTML: {HTML_REPORT_FILEPATH}")
    print("="*80)

    generate_html_report(JSONL_REPORT_FILEPATH, HTML_REPORT_FILEPATH)
