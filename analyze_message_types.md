# Message Content Type Analyzer

Analyzes the distribution and timing of messageContentType values in JSONL telemetry data.

## Basic Usage

### Unix/Linux/Mac

```bash
python analysis/src/analyze_message_types.py data.jsonl
```

### Windows (PowerShell)

```powershell
python analysis/src/analyze_message_types.py data.jsonl
```

### Windows (cmd)

```cmd
python analysis/src/analyze_message_types.py data.jsonl
```

## With Custom Output Directory

### Unix/Linux/Mac

```bash
python analysis/src/analyze_message_types.py data.jsonl \
  --output-dir ./analysis
```

### Windows (PowerShell)

```powershell
python analysis/src/analyze_message_types.py data.jsonl `
  --output-dir ./analysis
```

### Windows (cmd)

```cmd
python analysis/src/analyze_message_types.py data.jsonl --output-dir ./analysis
```

## Skip PNG Generation

### Unix/Linux/Mac

```bash
python analysis/src/analyze_message_types.py data.jsonl \
  --no-png
```

### Windows (PowerShell)

```powershell
python analysis/src/analyze_message_types.py data.jsonl `
  --no-png
```

### Windows (cmd)

```cmd
python analysis/src/analyze_message_types.py data.jsonl --no-png
```

## Specify Encoding

### Unix/Linux/Mac

```bash
python analysis/src/analyze_message_types.py data.jsonl \
  --encoding utf-16
```

### Windows (PowerShell)

```powershell
python analysis/src/analyze_message_types.py data.jsonl `
  --encoding utf-16
```

### Windows (cmd)

```cmd
python analysis/src/analyze_message_types.py data.jsonl --encoding utf-16
```

## Complete Example

### Unix/Linux/Mac

```bash
python analysis/src/analyze_message_types.py data/couchdb_export_20260126_112255.jsonl \
  --output-dir ./output \
  --encoding utf-16
```

### Windows (PowerShell)

```powershell
python analysis/src/analyze_message_types.py data/couchdb_export_20260126_112255.jsonl `
  --output-dir ./output `
  --encoding utf-16
```

### Windows (cmd)

```cmd
python analysis/src/analyze_message_types.py data/couchdb_export_20260126_112255.jsonl --output-dir ./output --encoding utf-16
```

## Output Files

The script generates the following files:

1. **CSV File**: `{filename}_message_type_analysis.csv`

   - Contains all statistics in tabular format
   - Columns: Message Type, Count, Percentage, Avg Interval (seconds), Avg Interval, First Appearance, Last Appearance

2. **HTML Table**: `{filename}_message_type_table.html`

   - Interactive table showing distribution and timing

3. **HTML Chart**: `{filename}_message_type_chart.html`

   - Bar chart visualization of message type counts

4. **PNG Table** (optional): `{filename}_message_type_table.png`

   - Static image of the table

5. **PNG Chart** (optional): `{filename}_message_type_chart.png`
   - Static image of the bar chart

## CSV Output Columns

| Column                 | Description                                 |
| ---------------------- | ------------------------------------------- |
| Message Type           | The messageContentType value                |
| Count                  | Number of occurrences in the dataset        |
| Percentage             | Percentage of total records                 |
| Avg Interval (seconds) | Average time between appearances in seconds |
| Avg Interval           | Human-readable interval (ms/sec/min/hr)     |
| First Appearance       | Timestamp of first occurrence               |
| Last Appearance        | Timestamp of last occurrence                |

## Command Line Options

| Option         | Description                                    | Default           |
| -------------- | ---------------------------------------------- | ----------------- |
| `jsonl_file`   | Path to the JSONL file (required)              | -                 |
| `--output-dir` | Output directory for generated files           | Current directory |
| `--encoding`   | File encoding (auto, utf-8, utf-16, utf-16-le) | auto              |
| `--no-png`     | Skip PNG generation                            | False             |

## Examples by Use Case

### Quick Analysis (Console Output Only)

```bash
python analysis/src/analyze_message_types.py data.jsonl
```

### Full Analysis with All Outputs

```bash
python analysis/src/analyze_message_types.py data.jsonl --output-dir ./reports
```

### Large Dataset (Skip PNG for Speed)

```bash
python analysis/src/analyze_message_types.py large_data.jsonl --no-png --output-dir ./output
```

### UTF-16 Encoded File

```bash
python analysis/src/analyze_message_types.py data.jsonl --encoding utf-16 --output-dir ./output
```

## Interpreting Results

**Count**: Shows how frequently each message type appears

- Higher count = more frequent message type

**Percentage**: Shows the proportion of each message type in the dataset

- Helps identify dominant message types

**Average Interval**: Shows the typical time between consecutive messages of the same type

- Shorter interval = messages appear more frequently
- Longer interval = messages appear less frequently
- "N/A" = only one occurrence found

**Example Interpretation**:

```
Message Type: Remoot.SS139OutsideControlMessage
Count: 15,234
Percentage: 45.2%
Avg Interval: 125.5 ms

This message appears very frequently (45% of all messages)
and occurs approximately every 125 milliseconds.
```

## Troubleshooting

### "No data loaded" or "0 records"

- Check file encoding with `--encoding utf-16` or `--encoding utf-8`
- Verify the file is valid JSONL format (one JSON object per line)

### PNG export fails

- Install kaleido: `pip install kaleido`
- Or use `--no-png` to skip PNG generation
- HTML files will still be created

### Large file processing is slow

- Use `--no-png` to speed up processing
- The script will still generate CSV and HTML outputs
