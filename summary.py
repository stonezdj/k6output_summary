import pandas as pd
import os

if len(os.sys.argv) < 2:
    print("Usage: python summary.py <path_to_directory>")
    exit(1)

# Load CSV
directory = os.sys.argv[1]

csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
if not csv_files:
    print("No CSV files found in the specified directory.")
    exit(1)

# List to store summary data
summary_data = []

for file_name in csv_files:
    # print(f"Processing file: {file_name}")
    try:
        df = pd.read_csv(file_name)

        # Filter only http_req_duration metric
        reqs = df[ (df['metric_name'] == 'iteration_duration') & (df['scenario'] == 'default') ].copy()

        # Total requests
        total_reqs = df[df['metric_name'] == 'success']['metric_value'].count()
        print(f"total request count: {total_reqs}")

        # Failed requests
        failed_reqs = df[ (df['metric_name'] == 'success') & (df['metric_value'] == 0 ) ]['metric_value'].count()
        print(f"failed request count: {failed_reqs}")

        # Convert ms to seconds if needed
        reqs['metric_value'] = reqs['metric_value'] / 1000.0

        # Summary stats
        summary = {
            "test case": os.path.splitext(os.path.basename(file_name))[0],
            "count": len(reqs),
            "avg": round(reqs['metric_value'].mean(),2),
            "min": round(reqs['metric_value'].min(),2),
            "max": round(reqs['metric_value'].max(),2),
            "p90": round(reqs['metric_value'].quantile(0.90),2),
            "p95": round(reqs['metric_value'].quantile(0.95),2),
            "success rate": round((total_reqs - failed_reqs) * 100 / total_reqs if total_reqs > 0 else 0, 2),
        }

        file_base_name = os.path.splitext(os.path.basename(file_name))[0]
        print(f"Summary for {file_base_name}:")
        print(summary)
        print("-" * 100)
        summary_data.append((summary))

    except Exception as e:
        print(f"Error processing file {file_name}: {e}")

# Create a DataFrame from the summary data
summary_df = pd.DataFrame(summary_data)

# Export the DataFrame to an HTML file
output_html = os.path.join(directory, "summary.html")
summary_df.to_html(output_html, index=False)

print(f"Summary has been written to {output_html}")
