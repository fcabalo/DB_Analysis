import json
import pandas as pd
import plotly.graph_objects as go
import argparse
import os
from datetime import datetime
from collections import defaultdict

# ============================================================
# COMMAND LINE ARGUMENT PARSING
# ============================================================

parser = argparse.ArgumentParser(
    description="Analyze messageContentType distribution and timing in JSONL telemetry data"
)

parser.add_argument("jsonl_file", type=str, help="Path to the JSONL file")
parser.add_argument(
    "--output-dir",
    type=str,
    default=".",
    help="Output directory for generated files (default: current directory)",
)
parser.add_argument(
    "--encoding",
    type=str,
    default="auto",
    choices=["auto", "utf-8", "utf-16", "utf-16-le"],
    help="File encoding (default: auto-detect)",
)
parser.add_argument("--png", action="store_true", help="Skip PNG generation")

args = parser.parse_args()

# ============================================================
# LOAD JSONL FILE
# ============================================================

print(f"Loading JSONL file: {args.jsonl_file}")

# Determine encoding
if args.encoding == "auto":
    # Quick check for UTF-16 BOM
    with open(args.jsonl_file, "rb") as f:
        first_bytes = f.read(2)
        if first_bytes == b"\xff\xfe":
            encoding = "utf-16-le"
            print(f"Detected encoding: utf-16-le (BOM found)")
        else:
            encoding = "utf-8"
            print(f"Using encoding: utf-8")
else:
    encoding = args.encoding
    print(f"Using specified encoding: {encoding}")

# Load data and analyze
message_type_data = defaultdict(lambda: {"count": 0, "timestamps": []})

total_records = 0
print("Processing records...")

with open(args.jsonl_file, "r", encoding=encoding, errors="ignore") as f:
    for line_num, line in enumerate(f, 1):
        if line_num % 10000 == 0:
            print(
                f"  Processed {line_num} lines... ({len(message_type_data)} unique message types)"
            )

        line = line.strip()
        if not line:
            continue

        try:
            obj = json.loads(line)
            total_records += 1

            # Get message type and timestamp
            msg_type = obj.get("messageContentType", "UNKNOWN")
            timestamp_str = obj.get("timestamp")

            # Update count
            message_type_data[msg_type]["count"] += 1

            # Parse timestamp if available
            if timestamp_str:
                try:
                    timestamp = pd.to_datetime(timestamp_str)
                    message_type_data[msg_type]["timestamps"].append(timestamp)
                except:
                    pass

        except json.JSONDecodeError as e:
            if line_num <= 5:
                print(f"Warning: Skipping invalid JSON on line {line_num}")
            continue

print(f"\nLoaded {total_records} records")
print(f"Found {len(message_type_data)} unique message types")

# ============================================================
# CALCULATE STATISTICS
# ============================================================

print("\nCalculating statistics...")

results = []

for msg_type, data_dict in message_type_data.items():
    count = data_dict["count"]
    timestamps = data_dict["timestamps"]

    # Calculate average time between appearances
    avg_interval_seconds = None
    avg_interval_str = "N/A"
    first_appearance = None
    last_appearance = None

    if len(timestamps) > 0:
        # Sort timestamps first
        timestamps_sorted = sorted(timestamps)
        first_appearance = timestamps_sorted[0]
        last_appearance = timestamps_sorted[-1]
        
        intervals = []
        # Calculate intervals only if we have more than one timestamp
        if len(timestamps_sorted) > 1:
            for i in range(1, len(timestamps_sorted)):
                interval = (
                    timestamps_sorted[i] - timestamps_sorted[i - 1]
                ).total_seconds()
                intervals.append(interval)

            if intervals:
                avg_interval_seconds = sum(intervals) / len(intervals)

                # Format nicely
                if avg_interval_seconds < 1:
                    avg_interval_str = f"{avg_interval_seconds*1000:.2f} ms"
                elif avg_interval_seconds < 60:
                    avg_interval_str = f"{avg_interval_seconds:.2f} sec"
                elif avg_interval_seconds < 3600:
                    avg_interval_str = f"{avg_interval_seconds/60:.2f} min"
                else:
                    avg_interval_str = f"{avg_interval_seconds/3600:.2f} hr"

    results.append(
        {
            "Message Type": msg_type,
            "Count": count,
            "Percentage": (count / total_records) * 100 if total_records > 0 else 0,
            "Avg Interval (seconds)": avg_interval_seconds,
            "Avg Interval": avg_interval_str,
            "First Appearance": first_appearance,
            "Last Appearance": last_appearance,
            "Timestamp": timestamps_sorted,
            "Intervals": [avg_interval_seconds] + intervals
        }
    )

# Create DataFrame
df_results = pd.DataFrame(results)

# Sort by count (descending)
df_results = df_results.sort_values("Count", ascending=False)

print(f"\nMessage Type Distribution:")
print(
    df_results[["Message Type", "Count", "Percentage", "Avg Interval"]].to_string(
        index=False
    )
)

# ============================================================
# EXPORT CSV
# ============================================================

base_filename = os.path.splitext(os.path.basename(args.jsonl_file))[0]
output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)

csv_file = os.path.join(output_dir, f"{base_filename}_message_type_analysis.csv")
df_results.to_csv(csv_file, index=False)
print(f"\nExported analysis to {csv_file}")

# ============================================================
# CREATE VISUALIZATIONS
# ============================================================

print("\nGenerating visualizations...")

# Create a table figure
fig = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=["Message Type", "Count", "Percentage (%)", "Avg Interval"],
                fill_color="paleturquoise",
                align="left",
                font=dict(size=12, color="black"),
            ),
            cells=dict(
                values=[
                    df_results["Message Type"],
                    df_results["Count"],
                    df_results["Percentage"].round(2),
                    df_results["Avg Interval"],
                ],
                fill_color="lavender",
                align="left",
                font=dict(size=11),
            ),
        )
    ]
)

fig.update_layout(
    title=f"Message Type Distribution - {base_filename}",
    height=max(400, len(df_results) * 30 + 100),
)

# Save HTML
output_file_html = os.path.join(output_dir, f"{base_filename}_message_type_table.html")
fig.write_html(output_file_html)
print(f"Table saved as {output_file_html}")

# Create bar chart
fig_bar = go.Figure()

fig_bar.add_trace(
    go.Bar(
        x=df_results["Message Type"],
        y=df_results["Count"],
        text=df_results["Count"],
        textposition="auto",
        marker_color="indianred",
    )
)

fig_bar.update_layout(
    title=f"Message Type Count Distribution - {base_filename}",
    xaxis_title="Message Type",
    yaxis_title="Count",
    height=600,
    xaxis_tickangle=-45,
)

# Save bar chart HTML
output_file_bar_html = os.path.join(
    output_dir, f"{base_filename}_message_type_chart.html"
)
fig_bar.write_html(output_file_bar_html)
print(f"Chart saved as {output_file_bar_html}")

# Create scatter plot
fig_scatter = go.Figure()

for result in results:
    fig_scatter.add_trace(
        go.Scatter(
            x=result["Timestamp"],
            y=result["Intervals"],
            mode='markers',
            name=result["Message Type"]
        )
    )

fig_scatter.update_layout(
    title=f"Message Type Intervals - {base_filename}",
    xaxis_title="Timestamp",
    yaxis_title="Interval(seconds)",
)

    # Save scatter plot HTML
output_file_scatter_html = os.path.join(
    output_dir, f"{base_filename}_message_type_scatter.html"
)
fig_scatter.write_html(output_file_scatter_html)
print(f"Chart saved as {output_file_scatter_html}")


# Save PNG if requested
if args.png:
    print("\nGenerating PNG files...")

    # Save table as PNG
    output_file_png = os.path.join(
        output_dir, f"{base_filename}_message_type_table.png"
    )
    try:
        import kaleido

        fig.write_image(
            output_file_png, width=1600, height=max(400, len(df_results) * 30 + 100)
        )
        print(f"Table saved as {output_file_png}")
    except Exception as e:
        print(f"Could not save table PNG: {str(e)}")

    # Save chart as PNG
    output_file_bar_png = os.path.join(
        output_dir, f"{base_filename}_message_type_chart.png"
    )
    try:
        import kaleido

        fig_bar.write_image(output_file_bar_png, width=1920, height=1080)
        print(f"Chart saved as {output_file_bar_png}")
    except Exception as e:
        print(f"Could not save chart PNG: {str(e)}")

print("\n=== Analysis Complete ===")
print(f"Total records: {total_records}")
print(f"Unique message types: {len(message_type_data)}")
if len(df_results) > 0:
    print(
        f"Most common: {df_results.iloc[0]['Message Type']} ({df_results.iloc[0]['Count']} occurrences)"
    )
