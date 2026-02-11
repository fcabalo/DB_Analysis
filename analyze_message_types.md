# Message Content Type Analyzer

Analyzes the distribution and timing of messageContentType values in JSONL telemetry data.

## Features

- Counts occurrences of each messageContentType
- Calculates average time intervals between messages of the same type
- Generates interactive HTML tables and charts
- Exports detailed CSV analysis
- Progress indicators for large files
- Automatic encoding detection

## Basic Usage

### Unix/Linux/Mac

```bash
python analyze_message_types.py data.jsonl
```

### Windows (PowerShell)

```powershell
python analyze_message_types.py data.jsonl
```

### Windows (cmd)

```cmd
python analyze_message_types.py data.jsonl
```

## With Custom Output Directory

### Unix/Linux/Mac

```bash
python analyze_message_types.py data.jsonl \
  --output-dir ./analysis
```

### Windows (PowerShell)

```powershell
python analyze_message_types.py data.jsonl `
  --output-dir ./analysis
```

### Windows (cmd)

```cmd
python analyze_message_types.py data.jsonl --output-dir ./analysis
```

## Enable PNG Generation

### Unix/Linux/Mac

```bash
python analyze_message_types.py data.jsonl \
  --png
```

### Windows (PowerShell)

```powershell
python analyze_message_types.py data.jsonl `
  --png
```

### Windows (cmd)

```cmd
python analyze_message_types.py data.jsonl --png
```

**Note:** PNG generation is **disabled by default** for faster processing. Use `--png` to enable it.

## Specify Encoding

### Unix/Linux/Mac

```bash
python analyze_message_types.py data.jsonl \
  --encoding utf-16
```

### Windows (PowerShell)

```powershell
python analyze_message_types.py data.jsonl `
  --encoding utf-16
```

### Windows (cmd)

```cmd
python analyze_message_types.py data.jsonl --encoding utf-16
```

## Complete Example

### Unix/Linux/Mac

```bash
python analyze_message_types.py data/couchdb_export_20260126_112255.jsonl \
  --output-dir ./output \
  --encoding utf-16
```

### Windows (PowerShell)

```powershell
python analyze_message_types.py data/couchdb_export_20260126_112255.jsonl `
  --output-dir ./output `
  --encoding utf-16
```

### Windows (cmd)

```cmd
python analyze_message_types.py data/couchdb_export_20260126_112255.jsonl --output-dir ./output --encoding utf-16
```

## Recommended Usage for Large Files (100k+ records)

### Unix/Linux/Mac

```bash
python analyze_message_types.py data/large_file.jsonl \
  --output-dir ./output \
  --encoding auto
```

### Windows (PowerShell)

```powershell
python analyze_message_types.py data/large_file.jsonl `
  --output-dir ./output `
  --encoding auto
```

### Windows (cmd)

```cmd
python analyze_message_types.py data/large_file.jsonl --output-dir ./output --encoding auto
```

**Default behavior for faster processing:**

- PNG generation is disabled by default
- HTML files are still created and are interactive
- Significantly faster processing
- Add `--png` flag only if you need static images

## Output Files

The script generates the following files:

1. **CSV File**: `{filename}_message_type_analysis.csv`

   - Contains all statistics in tabular format
   - Columns: Message Type, Count, Percentage, Avg Interval (seconds), Avg Interval, First Appearance, Last Appearance

2. **HTML Table**: `{filename}_message_type_table.html`

   - Interactive table showing distribution and timing
   - Sortable columns
   - Can be opened in any web browser

3. **HTML Chart**: `{filename}_message_type_chart.html`

   - Bar chart visualization of message type counts
   - Interactive hover tooltips
   - Can be opened in any web browser

4. **PNG Table** (optional): `{filename}_message_type_table.png`

   - Static image of the table
   - Requires kaleido package
   - Generated only with `--png` flag

5. **PNG Chart** (optional): `{filename}_message_type_chart.png`
   - Static image of the bar chart
   - Requires kaleido package
   - Generated only with `--png` flag

## CSV Output Columns

| Column                 | Description                                 | Example                             |
| ---------------------- | ------------------------------------------- | ----------------------------------- |
| Message Type           | The messageContentType value                | `Remoot.SS139OutsideControlMessage` |
| Count                  | Number of occurrences in the dataset        | `15234`                             |
| Percentage             | Percentage of total records                 | `45.23`                             |
| Avg Interval (seconds) | Average time between appearances in seconds | `0.125`                             |
| Avg Interval           | Human-readable interval (ms/sec/min/hr)     | `125.50 ms`                         |
| First Appearance       | Timestamp of first occurrence               | `2026-01-26 07:00:00`               |
| Last Appearance        | Timestamp of last occurrence                | `2026-01-26 12:00:00`               |

## Command Line Options

| Option         | Type     | Description                                           | Default                 |
| -------------- | -------- | ----------------------------------------------------- | ----------------------- |
| `jsonl_file`   | Required | Path to the JSONL file                                | -                       |
| `--output-dir` | Optional | Output directory for generated files                  | Current directory (`.`) |
| `--encoding`   | Optional | File encoding: `auto`, `utf-8`, `utf-16`, `utf-16-le` | `auto`                  |
| `--png`        | Flag     | Enable PNG generation (disabled by default)           | False                   |

## Examples by Use Case

### Quick Analysis (Default - Fastest)

```bash
# Default mode - only generates CSV and HTML (no PNG)
python analyze_message_types.py data.jsonl
```

### Full Analysis with PNG Images

```bash
# Generates CSV, HTML, and PNG files
python analyze_message_types.py data.jsonl --output-dir ./reports --png
```

### Large Dataset (Optimized for Speed)

```bash
# Default behavior - PNG disabled for faster processing
python analyze_message_types.py large_data.jsonl --output-dir ./output
```

### UTF-16 Encoded File

```bash
# Explicitly specify UTF-16 encoding
python analyze_message_types.py data.jsonl --encoding utf-16 --output-dir ./output
```

### Production Use with PNG Export

```bash
# Organized output with all files including PNG
python analyze_message_types.py data.jsonl --output-dir ./reports/$(date +%Y%m%d) --png
```

## Progress Indicators

The script shows progress every 10,000 lines:

```
Processing records...
  Processed 10000 lines... (5 unique message types)
  Processed 20000 lines... (8 unique message types)
  Processed 30000 lines... (12 unique message types)
```

This helps you monitor processing of large files.

## Interpreting Results

### Count

Shows how frequently each message type appears

- **Higher count** = more frequent message type
- **Lower count** = less frequent message type

### Percentage

Shows the proportion of each message type in the dataset

- Helps identify dominant message types
- Sum of all percentages = 100%

### Average Interval

Shows the typical time between consecutive messages of the same type

- **Shorter interval** = messages appear more frequently
- **Longer interval** = messages appear less frequently
- **"N/A"** = only one occurrence found (no interval to calculate)

### Example Interpretation

```
Message Type: Remoot.SS139OutsideControlMessage
Count: 15,234
Percentage: 45.2%
Avg Interval: 125.5 ms

Interpretation:
This message type is very frequent, representing almost half of all messages
(45.2%). Messages of this type appear approximately every 125 milliseconds,
indicating high-frequency telemetry data.
```

```
Message Type: RemoteSupervisionAdapterHeartbeat
Count: 120
Percentage: 0.4%
Avg Interval: 5.00 sec

Interpretation:
This message type is infrequent (less than 1% of all messages) and appears
approximately every 5 seconds, suggesting it's a periodic heartbeat signal.
```

## Performance Tips

### For Large Files (100k+ records)

1. Default mode is already optimized (PNG disabled)
2. Use `--encoding utf-16` if you know the encoding (faster than auto-detect)
3. Consider processing on a machine with more RAM
4. Only add `--png` if you specifically need static images

### For Very Large Files (1M+ records)

1. PNG is disabled by default (optimal)
2. Specify exact encoding with `--encoding`
3. Monitor system memory usage
4. The CSV file will still contain all detailed statistics

### Typical Processing Times

- **10k records**: ~2-5 seconds
- **100k records**: ~15-30 seconds
- **1M records**: ~2-5 minutes
- **10M records**: ~20-40 minutes

_Times vary based on system performance and encoding. PNG generation adds minimal overhead when enabled._

## Troubleshooting

### "No data loaded" or "0 records"

**Cause**: File encoding mismatch or invalid JSONL format

**Solutions**:

- Try specifying encoding: `--encoding utf-16` or `--encoding utf-8`
- Verify the file is valid JSONL format (one JSON object per line)
- Check if file is actually UTF-16 by opening in text editor

### PNG export fails (when --png is used)

**Cause**: Kaleido package not installed or incompatible

**Solutions**:

- Install kaleido: `pip install kaleido`
- Or omit `--png` flag (HTML files are still created)
- HTML files are interactive and often better than static PNG
- Upgrade packages: `pip install --upgrade plotly kaleido`

### Large file processing is slow

**Cause**: Encoding detection overhead

**Solutions**:

- PNG is already disabled by default (optimal)
- Specify exact encoding: `--encoding utf-16`
- The CSV and HTML outputs will still be generated quickly

### Script appears stuck

**Cause**: Processing large file with many records

**Solutions**:

- Wait for progress indicators (printed every 10,000 lines)
- Check task manager to confirm script is running
- For very large files, consider processing on more powerful hardware

### Out of memory errors

**Cause**: Storing all timestamps for very large datasets

**Solutions**:

- Close other applications to free up RAM
- Process on a machine with more memory
- The script currently loads all timestamps into memory for accurate interval calculation

## Technical Details

### Encoding Detection

The script auto-detects encoding by:

1. Checking for UTF-16 BOM (Byte Order Mark) at file start
2. If BOM found (`\xff\xfe`), uses UTF-16-LE
3. Otherwise defaults to UTF-8

### Timestamp Parsing

- Uses pandas `to_datetime()` for robust parsing
- Handles multiple timestamp formats automatically
- Invalid timestamps are skipped gracefully

### Interval Calculation

Average interval is calculated as:

```
sum(all intervals between consecutive timestamps) / number of intervals
```

Only calculated when 2+ timestamps are available.

## Example Output

### Console Output

```
Loading JSONL file: data.jsonl
Using encoding: utf-16-le (BOM found)
Processing records...
  Processed 10000 lines... (12 unique message types)
  Processed 20000 lines... (15 unique message types)

Loaded 25000 records
Found 18 unique message types

Calculating statistics...

Message Type Distribution:
                                         Message Type  Count  Percentage Avg Interval
                     Remoot.SS139OutsideControlMessage  11234       44.94      125.5 ms
                   Remoot.SS139OutsideTelemetryMessage   8456       33.82      150.2 ms
      rse.ato.communication.ss139.telegrams.TrainControl   3421       13.68      350.8 ms
                                             UNKNOWN    1889        7.56          N/A

Exported analysis to output/data_message_type_analysis.csv
Table saved as output/data_message_type_table.html
Chart saved as output/data_message_type_chart.html

=== Analysis Complete ===
Total records: 25000
Unique message types: 18
Most common: Remoot.SS139OutsideControlMessage (11234 occurrences)
```

## Integration with Other Scripts

This script works well with the telemetry plotting script:

1. **First**: Run message type analyzer to understand your data

```bash
   python analyze_message_types.py data.jsonl --output-dir ./analysis
```

2. **Review**: Check the CSV or HTML output to identify relevant message types

3. **Then**: Use the plotting script to visualize specific fields

```bash
   python plot_data_plotly.py data.jsonl \
     --message-types "Remoot.SS139OutsideControlMessage" \
     --fields ActivatedHornHigh ActivatedHornLow
```

## Version History

### v1.2 (Current)

- Changed PNG generation to opt-in with `--png` flag (disabled by default)
- Improved performance for default usage
- Added progress indicators for large files
- Fixed timestamp sorting bug
- Improved encoding detection
- Better error handling
- Optimized memory usage

### v1.1

- Added progress indicators for large files
- Fixed timestamp sorting bug
- Improved encoding detection
- Better error handling
- Optimized memory usage

### v1.0 (Initial)

- Basic message type counting
- Average interval calculation
- CSV and HTML exports
