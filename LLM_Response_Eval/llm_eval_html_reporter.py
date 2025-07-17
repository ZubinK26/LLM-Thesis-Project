import json
import os
import sys
from datetime import datetime

# --- Global File Paths ---
BASE_DIR = r"C:\Users\ja\Documents\LLM_Eval"
LLM_RESPONSE_EVAL_DIR = os.path.join(BASE_DIR, "LLM_Response_Eval")
LLM_EVAL_REPORT_JSONL = os.path.join(LLM_RESPONSE_EVAL_DIR, "llm_eval_report.jsonl")
LLM_EVAL_REPORT_HTML = os.path.join(LLM_RESPONSE_EVAL_DIR, "llm_eval_report.html")

def generate_html_report():
    """
    Reads the llm_eval_report.jsonl file and generates an HTML report.
    """
    print(f"Attempting to generate HTML report from: {LLM_EVAL_REPORT_JSONL}")

    if not os.path.exists(LLM_EVAL_REPORT_JSONL):
        print(f"Error: JSONL report file not found at '{LLM_EVAL_REPORT_JSONL}'. Please run run_llm_evaluation.py first.", file=sys.stderr)
        sys.exit(1)

    evaluation_data = []
    try:
        with open(LLM_EVAL_REPORT_JSONL, 'r', encoding='utf-8') as f:
            for line in f:
                evaluation_data.append(json.loads(line.strip()))
        print(f"Successfully loaded {len(evaluation_data)} evaluation records.")
    except Exception as e:
        print(f"Error loading JSONL data from '{LLM_EVAL_REPORT_JSONL}': {e}", file=sys.stderr)
        sys.exit(1)

    if not evaluation_data:
        print("No evaluation data found to generate report. Exiting.", file=sys.stderr)
        sys.exit(0)

    # --- Start HTML Generation ---
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Response Evaluation Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            margin: 20px;
            background-color: #f4f7f6;
            color: #333;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            font-weight: 700;
        }}
        .report-info {{
            text-align: center;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #555;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            border-radius: 8px;
            overflow: hidden; /* Ensures rounded corners apply to table content */
            font-size: 0.9em;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 10px 12px;
            text-align: left;
            vertical-align: top;
        }}
        th {{
            background-color: #e0f2f7; /* Light blue header */
            color: #2c3e50;
            font-weight: bold;
            position: sticky;
            top: 0;
            z-index: 1; /* Keep headers visible on scroll */
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .response-cell {{
            max-height: 150px; /* Limit height for scrollable content */
            overflow-y: auto; /* Enable vertical scrolling */
            white-space: pre-wrap; /* Preserve whitespace and wrap text */
            word-wrap: break-word; /* Break long words */
            font-family: 'Roboto Mono', monospace; /* Monospace for code/response text */
            background-color: #fcfcfc;
            border-radius: 5px;
            padding: 8px;
            border: 1px solid #eee;
        }}
        .score-high {{ color: #28a745; font-weight: 600; }} /* Green */
        .score-medium {{ color: #ffc107; font-weight: 600; }} /* Orange/Yellow */
        .score-low {{ color: #dc3545; font-weight: 600; }} /* Red */
        .score-na {{ color: #6c757d; }} /* Grey */
        .compliant-true {{ color: #28a745; font-weight: 600; }}
        .compliant-false {{ color: #dc3545; font-weight: 600; }}
        .boolean-true {{ color: #28a745; font-weight: 600; }}
        .boolean-false {{ color: #dc3545; font-weight: 600; }}
        .warning {{ color: #ffc107; font-weight: 600; }}
        .error {{ color: #dc3545; font-weight: 600; }}

        /* Responsive adjustments */
        @media (max-width: 768px) {{
            body {{ margin: 10px; }}
            .container {{ padding: 15px; }}
            table, thead, tbody, th, td, tr {{
                display: block;
            }}
            thead tr {{
                position: absolute;
                top: -9999px;
                left: -9999px;
            }}
            tr {{ border: 1px solid #ccc; margin-bottom: 15px; border-radius: 8px; }}
            td {{
                border: none;
                border-bottom: 1px solid #eee;
                position: relative;
                padding-left: 50%;
                text-align: right;
            }}
            td:before {{
                position: absolute;
                top: 6px;
                left: 6px;
                width: 45%;
                padding-right: 10px;
                white-space: nowrap;
                text-align: left;
                font-weight: bold;
                color: #555;
            }}
            /* Data labels for responsive table */
            td:nth-of-type(1):before {{ content: "Query ID"; }}
            td:nth-of-type(2):before {{ content: "Model"; }}
            td:nth-of-type(3):before {{ content: "Run ID"; }}
            td:nth-of-type(4):before {{ content: "Query Text"; }}
            td:nth-of-type(5):before {{ content: "Constrained Response"; }}
            td:nth-of-type(6):before {{ content: "Unconstrained Response"; }}
            td:nth-of-type(7):before {{ content: "Expected Flags"; }}
            td:nth-of-type(8):before {{ content: "Detected Flags (Constrained)"; }}
            td:nth-of-type(9):before {{ content: "Detected Justifications (Raw)"; }}
            td:nth-of-type(10):before {{ content: "Recall Score"; }}
            td:nth-of-type(11):before {{ content: "Recall Class"; }}
            td:nth-of-type(12):before {{ content: "Precision Score"; }}
            td:nth-of-type(13):before {{ content: "Precision Class"; }}
            td:nth-of-type(14):before {{ content: "Total Flags"; }}
            td:nth-of-type(15):before {{ content: "Format Compliant"; }}
            td:nth-of-type(16):before {{ content: "Format Details"; }}
            td:nth-of-type(17):before {{ content: "Avg Words/Just."; }}
            td:nth-of-type(18):before {{ content: "Conciseness Class"; }}
            td:nth-of-type(19):before {{ content: "Hallucinated Rate"; }}
            td:nth-of-type(20):before {{ content: "Hallucination Class"; }}
            td:nth-of-type(21):before {{ content: "All Flags Covered"; }}
            td:nth-of-type(22):before {{ content: "Hedging Count"; }} /* NEW */
            /* Add more for placeholders if they become active columns */
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>LLM Response Evaluation Report</h1>
        <div class="report-info">
            Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Total Responses Evaluated: {len(evaluation_data)}
        </div>
        <table>
            <thead>
                <tr>
                    <th>Query ID</th>
                    <th>Model</th>
                    <th>Run ID</th>
                    <th>Query Text</th>
                    <th>Constrained Response</th>
                    <th>Unconstrained Response</th>
                    <th>Expected Flags</th>
                    <th>Detected Flags (Constrained)</th>
                    <th>Detected Justifications (Raw)</th>
                    <th>Recall Score</th>
                    <th>Recall Class</th>
                    <th>Precision Score</th>
                    <th>Precision Class</th>
                    <th>Total Flags</th>
                    <th>Format Compliant</th>
                    <th>Format Details</th>
                    <th>Avg Words/Just.</th>
                    <th>Conciseness Class</th>
                    <th>Hallucinated Rate</th>
                    <th>Hallucination Class</th>
                    <th>All Flags Covered</th>
                    <!-- Placeholder Columns -->
                    <th>Pause/Proceed Compliance</th>
                    <th>Justification Correctness</th>
                    <th>Explanation Readiness</th>
                    <th>Hedging Count</th> <!-- NEW HEADER -->
                </tr>
            </thead>
            <tbody>
    """

    # --- Populate Table Rows ---
    for record in evaluation_data:
        query_id = record.get('query_id', 'N/A')
        model_name = record.get('model_name', 'N/A')
        run_id = record.get('run_id', 'N/A')
        query_text = record.get('query_text', '')
        constrained_response_text = record.get('constrained_response_text', '')
        unconstrained_response_text = record.get('unconstrained_response_text', '')
        
        expected_flags = record.get('expected_assumptions_normalized', [])
        detected_flags = record.get('detected_flags_constrained_normalized', [])
        justifications = record.get('detected_justifications_constrained_raw', [])

        # Extracting results for each dimension
        constrained_eval = record.get('constrained_evaluation_results', {})
        unconstrained_eval = record.get('unconstrained_evaluation_results', {}) # NEW: Extract unconstrained results

        recall_data = constrained_eval.get('assumption_recall', {})
        recall_score = recall_data.get('recall_score', 'N/A')
        recall_class = recall_data.get('classification', 'N/A')

        precision_data = constrained_eval.get('assumption_precision', {})
        precision_score = precision_data.get('precision_score', 'N/A')
        precision_class = precision_data.get('classification', 'N/A')

        total_flags_data = constrained_eval.get('total_flags_count', {})
        total_flags_count = total_flags_data.get('total_flags_count', 'N/A')

        format_compliance_data = constrained_eval.get('format_compliance', {})
        format_compliant = format_compliance_data.get('compliant', 'N/A')
        format_details = format_compliance_data.get('details', 'N/A')

        conciseness_data = constrained_eval.get('justification_conciseness', {})
        avg_words_just = conciseness_data.get('average_words_per_justification', 'N/A')
        conciseness_class = conciseness_data.get('classification', 'N/A')

        hallucinated_data = constrained_eval.get('hallucinated_flag_rate', {})
        hallucinated_rate = hallucinated_data.get('hallucinated_rate', 'N/A')
        hallucination_class = hallucinated_data.get('classification', 'N/A')

        coverage_data = constrained_eval.get('coverage_all_flags_before_answering', {})
        all_flags_covered = coverage_data.get('all_flags_covered_before_answer', 'N/A')

        # NEW: Extract hedging count
        hedging_count_data = unconstrained_eval.get('hedging_count', {})
        hedging_count = hedging_count_data.get('hedging_count', 'N/A')

        # Placeholder data (still pulling from constrained_eval for now as per JSONL structure)
        pause_proceed_data = constrained_eval.get('pause_proceed_compliance', {})
        justification_correctness_data = constrained_eval.get('justification_correctness', {})
        explanation_readiness_data = constrained_eval.get('explanation_readiness', {})


        # Helper to get CSS class for scores/booleans
        def get_score_class(value):
            if isinstance(value, (float, int)):
                if value >= 0.8: return "score-high"
                elif value >= 0.5: return "score-medium"
                else: return "score-low"
            elif value == "High": return "score-high"
            elif value == "Medium": return "score-medium"
            elif value == "Low": return "score-low"
            elif value == "N/A (No expected flags)" or value == "N/A (No flags detected)" or value == "N/A (No justifications)" or value == "N/A": return "score-na"
            elif value is True: return "boolean-true"
            elif value is False: return "boolean-false"
            return ""

        html_content += f"""
                <tr>
                    <td>{query_id}</td>
                    <td>{model_name}</td>
                    <td>{run_id}</td>
                    <td><div class="response-cell">{query_text}</div></td>
                    <td><div class="response-cell">{constrained_response_text}</div></td>
                    <td><div class="response-cell">{unconstrained_response_text}</div></td>
                    <td><div class="response-cell">{', '.join(expected_flags) if expected_flags else 'None'}</div></td>
                    <td><div class="response-cell">{', '.join(detected_flags) if detected_flags else 'None'}</div></td>
                    <td><div class="response-cell">{'; '.join(justifications) if justifications else 'None'}</div></td>
                    <td class="{get_score_class(recall_score)}">{f'{recall_score:.2f}' if isinstance(recall_score, float) else recall_score}</td>
                    <td class="{get_score_class(recall_class)}">{recall_class}</td>
                    <td class="{get_score_class(precision_score)}">{f'{precision_score:.2f}' if isinstance(precision_score, float) else precision_score}</td>
                    <td class="{get_score_class(precision_class)}">{precision_class}</td>
                    <td>{total_flags_count}</td>
                    <td class="{get_score_class(format_compliant)}">{format_compliant}</td>
                    <td><div class="response-cell">{format_details}</div></td>
                    <td class="{get_score_class(avg_words_just)}">{f'{avg_words_just:.2f}' if isinstance(avg_words_just, float) else avg_words_just}</td>
                    <td class="{get_score_class(conciseness_class)}">{conciseness_class}</td>
                    <td class="{get_score_class(hallucinated_rate)}">{f'{hallucinated_rate:.2f}' if isinstance(hallucinated_rate, float) else hallucinated_rate}</td>
                    <td class="{get_score_class(hallucination_class)}">{hallucination_class}</td>
                    <td class="{get_score_class(all_flags_covered)}">{all_flags_covered}</td>
                    <!-- Placeholder Columns -->
                    <td>{pause_proceed_data.get('compliant', 'N/A')}</td>
                    <td>{justification_correctness_data.get('correctness_ratio', 'N/A')}</td>
                    <td>{explanation_readiness_data.get('ready', 'N/A')}</td>
                    <td>{hedging_count}</td> <!-- NEW DATA CELL -->
                </tr>
        """
    html_content += """
            </tbody>
        </table>
    </div>
    <script>
        // Ensure response text cells are scrollable
        document.addEventListener('DOMContentLoaded', function() {
            const responseCells = document.querySelectorAll('.response-cell');
            responseCells.forEach(cell => {
                // Check if the content overflows and add a title for hover
                if (cell.scrollHeight > cell.clientHeight || cell.scrollWidth > cell.clientWidth) {
                    cell.title = "Scroll to view full content";
                }
            });
        });
    </script>
</body>
</html>
    """

    # --- Write HTML to file ---
    try:
        with open(LLM_EVAL_REPORT_HTML, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"HTML report successfully generated at: {LLM_EVAL_REPORT_HTML}")
    except Exception as e:
        print(f"Error writing HTML report to '{LLM_EVAL_REPORT_HTML}': {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    print("--- Running LLM Response Evaluation Framework: HTML Reporter ---")
    print("This script generates a user-friendly HTML report from the JSONL evaluation data.")
    print("="*80)
    print(f"Input JSONL File: {LLM_EVAL_REPORT_JSONL}")
    print(f"Output HTML File: {LLM_EVAL_REPORT_HTML}")
    print("="*80)
    generate_html_report()
