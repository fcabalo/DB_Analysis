import json
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
from collections import defaultdict
import argparse

# ============================================================
# COMMAND LINE ARGUMENT PARSING
# ============================================================

parser = argparse.ArgumentParser(
    description="Process JSONL telemetry data and create timeseries visualizations"
)

# Required arguments
parser.add_argument("jsonl_file", type=str, help="Path to the JSONL file")

# Optional arguments for filtering and field selection
parser.add_argument(
    "--message-types",
    type=str,
    nargs="+",
    help='Message content types to filter (e.g., "Remoot.SS139OutsideControlMessage")',
    default=[],
)
parser.add_argument(
    "--fields",
    type=str,
    nargs="+",
    help='Field names to extract and plot (e.g., "ActivatedHornHigh" "ThreewaySwitchState")',
    default=[],
)
parser.add_argument(
    "--field-paths",
    type=str,
    nargs="+",
    help='JSON paths to fields (e.g., "message.OutsideControlData.ActivatedHornHigh" "message.MessagePayload.ThreewaySwitchState")',
    default=[],
)
parser.add_argument(
    "--max-points",
    type=int,
    default=1000,
    help="Maximum number of points for visualization (default: 1000)",
)
parser.add_argument(
    "--output-dir",
    type=str,
    default=".",
    help="Output directory for generated files (default: current directory)",
)
parser.add_argument(
    "--png", action="store_true", help="Generate PNG images (default: disabled)"
)
parser.add_argument("--no-csv", action="store_true", help="Skip CSV exports")
parser.add_argument(
    "--lightweight",
    action="store_true",
    help="Generate lightweight HTML (no markers, simplified features)",
)
parser.add_argument(
    "--encoding",
    type=str,
    default="auto",
    choices=["auto", "utf-8", "utf-16", "utf-16-le"],
    help="File encoding (default: auto-detect)",
)

args = parser.parse_args()

# ============================================================
# HELPER FUNCTIONS
# ============================================================


def get_nested_value(obj, path):
    """
    Get value from nested dictionary using dot notation path
    Example: get_nested_value(data, "message.OutsideControlData.ActivatedHornHigh")
    """
    keys = path.split(".")
    value = obj
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return None
        else:
            return None
    return value


def auto_detect_encoding(filepath):
    """Auto-detect file encoding"""
    encodings_to_try = ["utf-16", "utf-16-le", "utf-8"]

    for encoding in encodings_to_try:
        try:
            with open(filepath, "r", encoding=encoding, errors="ignore") as f:
                # Try to read first few lines
                for _ in range(3):
                    line = f.readline()
                    if line:
                        json.loads(line.strip())
                print(f"Detected encoding: {encoding}")
                return encoding
        except:
            continue

    # Default fallback
    print("Could not auto-detect encoding, using utf-8")
    return "utf-8"


# ============================================================
# LOAD JSONL FILE
# ============================================================

print(f"Loading JSONL file: {args.jsonl_file}")

# Determine encoding
if args.encoding == "auto":
    encoding = auto_detect_encoding(args.jsonl_file)
else:
    encoding = args.encoding
    print(f"Using specified encoding: {encoding}")

# Load data
data = []
with open(args.jsonl_file, "r", encoding=encoding, errors="ignore") as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if not line:  # Skip empty lines
            continue
        try:
            obj = json.loads(line)
            data.append(obj)
        except json.JSONDecodeError as e:
            if line_num <= 3:  # Show first few errors
                print(
                    f"Warning: Skipping invalid JSON on line {line_num}: {str(e)[:80]}"
                )
            continue

print(f"Loaded {len(data)} records")

# ============================================================
# EXTRACT DATA BASED ON PARAMETERS
# ============================================================

# If no message types specified, process all records
filter_by_message_type = len(args.message_types) > 0

# If no fields specified, try to auto-detect common fields
if len(args.fields) == 0 and len(args.field_paths) == 0:
    print(
        "No fields specified. Please use --fields or --field-paths to specify which data to extract."
    )
    exit(1)

records_by_timestamp = defaultdict(dict)
extracted_field_names = set()

for item in data:
    msg_type = item.get("messageContentType", "")

    # Filter by message type if specified
    if filter_by_message_type:
        if not any(mt in msg_type for mt in args.message_types):
            continue

    timestamp = item.get("timestamp")
    if not timestamp:
        continue

    # Initialize record
    if "timestamp" not in records_by_timestamp[timestamp]:
        records_by_timestamp[timestamp]["timestamp"] = timestamp
        records_by_timestamp[timestamp]["messageContentType"] = msg_type

    # Extract fields using paths
    for field_path in args.field_paths:
        # Get the field name (last part of the path)
        field_name = field_path.split(".")[-1]
        value = get_nested_value(item, field_path)

        if value is not None:
            records_by_timestamp[timestamp][field_name] = value
            extracted_field_names.add(field_name)

    # Extract simple fields from common locations
    for field_name in args.fields:
        # Try multiple common locations
        value = None

        # Try message.MessagePayload
        if value is None:
            value = get_nested_value(item, f"message.MessagePayload.{field_name}")

        # Try message.OutsideControlData
        if value is None:
            value = get_nested_value(item, f"message.OutsideControlData.{field_name}")

        # Try direct in message
        if value is None:
            value = get_nested_value(item, f"message.{field_name}")
        
        # Try message.ActiveCabInfo (for Cab1/Cab2)
        if value is None:
            value = get_nested_value(item, f"message.ActiveCabInfo.{field_name}")

        if value is not None:
            records_by_timestamp[timestamp][field_name] = value
            extracted_field_names.add(field_name)

# Convert to list
records = list(records_by_timestamp.values())

print(f"Extracted {len(records)} records with relevant data")
print(f"Fields found: {', '.join(sorted(extracted_field_names))}")

if len(records) == 0:
    print("No data extracted. Check your message types and field names.")
    exit(1)

# ============================================================
# CREATE DATAFRAME AND PROCESS
# ============================================================

df = pd.DataFrame(records)

# Convert timestamp to datetime
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
df = df.sort_values("timestamp")

print(f"Processed {len(df)} relevant records")
print(f"Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")

# ============================================================
# DOWNSAMPLE DATA
# ============================================================


def downsample_with_state_changes(df, max_points=3000, value_columns=None):
    """Downsample data while preserving state changes"""
    if len(df) <= max_points:
        return df

    print(f"Downsampling from {len(df)} to ~{max_points} points...")

    indices_to_keep = set()
    indices_to_keep.add(0)
    indices_to_keep.add(len(df) - 1)

    # Find state changes
    if value_columns:
        for col in value_columns:
            if col in df.columns:
                for i in range(1, len(df)):
                    if df.iloc[i - 1][col] != df.iloc[i][col]:
                        indices_to_keep.add(i - 1)
                        indices_to_keep.add(i)

    remaining_points = max_points - len(indices_to_keep)
    if remaining_points > 0:
        step = len(df) // remaining_points
        for i in range(0, len(df), step):
            indices_to_keep.add(i)

    indices_list = sorted(list(indices_to_keep))
    downsampled = df.iloc[indices_list].copy()

    print(f"Downsampled to {len(downsampled)} points")
    return downsampled


# Get list of value columns (excluding timestamp and messageContentType)
value_columns = [
    col
    for col in df.columns
    if col not in ["timestamp", "messageContentType", "usecase"]
]

df_plot = downsample_with_state_changes(
    df, max_points=args.max_points, value_columns=value_columns
)

# Forward-fill to show last known state
print("Forward-filling values...")
for col in value_columns:
    if col in df_plot.columns:
        df_plot[col] = df_plot[col].ffill()

# ============================================================
# EXPORT CSV FILES
# ============================================================

if not args.no_csv:
    print("\nExporting CSV files...")

    base_filename = os.path.splitext(os.path.basename(args.jsonl_file))[0]
    output_dir = args.output_dir

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    csv_file = os.path.join(output_dir, f"{base_filename}_processed_data.csv")
    df.to_csv(csv_file, index=False)
    print(f"Exported full dataset to {csv_file}")

# ============================================================
# CREATE VISUALIZATIONS
# ============================================================

print("\nGenerating visualizations...")

base_filename = os.path.splitext(os.path.basename(args.jsonl_file))[0]
output_dir = args.output_dir
os.makedirs(output_dir, exist_ok=True)

# Analyze data types for each field
field_types = {}
for field_name in value_columns:
    if field_name not in df_plot.columns:
        continue

    # Get non-null values
    sample_values = df_plot[field_name].dropna()

    if len(sample_values) == 0:
        field_types[field_name] = "unknown"
        continue

    # Check data type
    unique_values = set(sample_values.unique())

    # Boolean check - check both actual booleans and numeric 0/1
    if sample_values.dtype == bool:
        field_types[field_name] = "boolean"
    elif unique_values.issubset({True, False}):
        field_types[field_name] = "boolean"
    elif unique_values.issubset({0, 1}) and len(unique_values) <= 2:
        field_types[field_name] = "boolean"
    elif unique_values.issubset({0.0, 1.0}) and len(unique_values) <= 2:
        field_types[field_name] = "boolean"
    # Numeric check
    elif pd.api.types.is_numeric_dtype(sample_values):
        field_types[field_name] = "numeric"
    # String check
    elif pd.api.types.is_string_dtype(sample_values):
        field_types[field_name] = "string"
    else:
        field_types[field_name] = "unknown"

print(f"Detected field types: {field_types}")

# Separate fields by type
boolean_fields = [k for k, v in field_types.items() if v == "boolean"]
numeric_fields = [k for k, v in field_types.items() if v == "numeric"]
string_fields = [k for k, v in field_types.items() if v == "string"]

# Create figure with secondary y-axis if we have both boolean and numeric fields
if len(boolean_fields) > 0 and len(numeric_fields) > 0:
    # Create figure with dual y-axes
    fig = make_subplots(specs=[[{"secondary_y": True}]])
else:
    # Single y-axis is fine
    fig = go.Figure()

# Plot each field based on its type
colors = [
    "red",
    "blue",
    "green",
    "orange",
    "purple",
    "brown",
    "pink",
    "gray",
    "olive",
    "cyan",
    "magenta",
    "teal",
    "navy",
    "maroon",
    "lime",
    "indigo",
    "coral",
    "gold",
    "crimson",
    "darkgreen",
]

idx = 0

# Plot boolean fields first (on primary y-axis or left side)
for field_name in sorted(boolean_fields):
    if field_name not in df_plot.columns:
        continue

    color = colors[idx % len(colors)]
    idx += 1

    # For boolean fields, convert to 0/1 for plotting
    y_values = []
    for val in df_plot[field_name]:
        if pd.isna(val):
            y_values.append(None)
        elif val == True or val == 1 or val == 1.0:
            y_values.append(1)
        else:
            y_values.append(0)

    trace = go.Scatter(
        x=df_plot["timestamp"],
        y=y_values,
        mode="lines",
        name=f"{field_name} (bool)",
        line=dict(color=color, width=4),
        connectgaps=False,
        hovertemplate="%{x}<br>" + field_name + ": %{y}<extra></extra>",
    )

    if len(boolean_fields) > 0 and len(numeric_fields) > 0:
        fig.add_trace(trace, secondary_y=False)
    else:
        fig.add_trace(trace)

# Plot numeric fields (on secondary y-axis or right side if we have boolean fields)
for field_name in sorted(numeric_fields):
    if field_name not in df_plot.columns:
        continue

    color = colors[idx % len(colors)]
    idx += 1

    # For numeric fields, show actual values with lines and markers
    if args.lightweight:
        # Lightweight mode: no markers
        trace = go.Scatter(
            x=df_plot["timestamp"],
            y=df_plot[field_name],
            mode="lines",
            name=f"{field_name} (num)",
            line=dict(color=color, width=2),
            hovertemplate="%{x}<br>" + field_name + ": %{y}<extra></extra>",
        )
    else:
        # Regular mode: with markers
        trace = go.Scatter(
            x=df_plot["timestamp"],
            y=df_plot[field_name],
            mode="lines+markers",
            name=f"{field_name} (num)",
            line=dict(color=color, width=2),
            marker=dict(size=4, color=color),
            hovertemplate="%{x}<br>" + field_name + ": %{y}<extra></extra>",
        )

    if len(boolean_fields) > 0 and len(numeric_fields) > 0:
        fig.add_trace(trace, secondary_y=True)
    else:
        fig.add_trace(trace)

# Plot string fields (convert to categorical on secondary y-axis)
for field_name in sorted(string_fields):
    if field_name not in df_plot.columns:
        continue

    color = colors[idx % len(colors)]
    idx += 1

    # For string fields, show as categorical (convert to numeric codes)
    # Get unique values and create a mapping
    unique_vals = df_plot[field_name].dropna().unique()
    val_to_num = {val: idx for idx, val in enumerate(unique_vals)}

    y_values = [
        val_to_num.get(val, None) if pd.notna(val) else None
        for val in df_plot[field_name]
    ]

    trace = go.Scatter(
        x=df_plot["timestamp"],
        y=y_values,
        mode="lines+markers",
        name=f"{field_name} (str)",
        line=dict(color=color, width=2),
        marker=dict(size=6, color=color),
        text=[str(val) if pd.notna(val) else "" for val in df_plot[field_name]],
        hovertemplate="%{x}<br>" + field_name + ": %{text}<extra></extra>",
    )

    if len(boolean_fields) > 0 and len(numeric_fields) > 0:
        fig.add_trace(trace, secondary_y=True)
    else:
        fig.add_trace(trace)

# Update layout based on mode
if args.lightweight:
    # Lightweight mode - smaller file size
    fig.update_layout(
        title=f"Telemetry Data: {base_filename}",
        xaxis_title="Time (UTC)",
        xaxis=dict(type="date"),
        hovermode="x unified",
        showlegend=True,
        height=700,
    )
    
    # Set y-axis titles and format boolean axis
    if len(boolean_fields) > 0 and len(numeric_fields) > 0:
        fig.update_yaxes(
            title_text="Boolean",
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['False', 'True'],
            secondary_y=False
        )
        fig.update_yaxes(title_text="Numeric Values", secondary_y=True)
    elif len(boolean_fields) > 0:
        fig.update_layout(
            yaxis=dict(
                title="Boolean",
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['False', 'True']
            )
        )
    elif len(numeric_fields) > 0:
        fig.update_layout(yaxis_title="Numeric Values")
    else:
        fig.update_layout(yaxis_title="Values")
    
    # Write with CDN mode for smaller file size
    config = {"displayModeBar": True, "displaylogo": False}
    fig.write_html(
        os.path.join(output_dir, f"{base_filename}_timeseries.html"),
        config=config,
        include_plotlyjs="cdn",
    )
    print(f"Graph saved as {os.path.join(output_dir, f'{base_filename}_timeseries.html')}")
else:
    # Regular mode - full features
    fig.update_layout(
        title=f"Telemetry Data: {base_filename}",
        xaxis_title="Time (UTC)",
        xaxis=dict(
            type="date",
            rangeslider=dict(visible=True),
            rangeselector=dict(
                buttons=list(
                    [
                        dict(count=1, label="1m", step="minute", stepmode="backward"),
                        dict(count=5, label="5m", step="minute", stepmode="backward"),
                        dict(count=15, label="15m", step="minute", stepmode="backward"),
                        dict(count=1, label="1h", step="hour", stepmode="backward"),
                        dict(step="all", label="All"),
                    ]
                )
            ),
        ),
        hovermode="x unified",
        showlegend=True,
        height=700,
    )
    
    # Set y-axis titles and format boolean axis
    if len(boolean_fields) > 0 and len(numeric_fields) > 0:
        fig.update_yaxes(
            title_text="Boolean",
            tickmode='array',
            tickvals=[0, 1],
            ticktext=['False', 'True'],
            secondary_y=False
        )
        fig.update_yaxes(title_text="Numeric Values", secondary_y=True)
    elif len(boolean_fields) > 0:
        fig.update_layout(
            yaxis=dict(
                title="Boolean",
                tickmode='array',
                tickvals=[0, 1],
                ticktext=['False', 'True']
            )
        )
    elif len(numeric_fields) > 0:
        fig.update_layout(yaxis_title="Numeric Values")
    else:
        fig.update_layout(yaxis_title="Values")
    
    # Save HTML
    output_file_html = os.path.join(output_dir, f"{base_filename}_timeseries.html")
    fig.write_html(output_file_html)
    print(f"Graph saved as {output_file_html}")

# Save PNG if requested
if args.png:
    output_file_png = os.path.join(output_dir, f"{base_filename}_timeseries.png")
    try:
        import kaleido

        print(f"Kaleido version: {kaleido.__version__}")
        print(f"Attempting to save PNG to: {output_file_png}")

        # Make sure the figure has data
        if len(fig.data) == 0:
            print("Warning: Figure has no data traces. Skipping PNG export.")
        else:
            fig.write_image(output_file_png, width=1920, height=1080, format="png")

            # Check if file was created
            if os.path.exists(output_file_png):
                file_size = os.path.getsize(output_file_png)
                print(f"Graph saved as {output_file_png} ({file_size} bytes)")
            else:
                print(f"PNG file was not created at {output_file_png}")

    except ImportError as e:
        print(f"Kaleido import error: {e}")
        print(f"Install with: pip install -U kaleido")
    except Exception as e:
        print(f"Could not save PNG. Error details:")
        print(f"  Error type: {type(e).__name__}")
        print(f"  Error message: {str(e)}")

print("\n=== Analysis Complete ===")
print(f"Total records processed: {len(df)}")
print(f"Records used for visualization: {len(df_plot)}")
print(f"Fields extracted: {', '.join(sorted(value_columns))}")
print(f"Field types: {field_types}")