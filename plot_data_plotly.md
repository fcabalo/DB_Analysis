# Using field paths (recommended - most explicit)

### Unix/Linux/Mac
```bash
python analysis/src/plot_data_plotly.py data.jsonl \
 --field-paths "message.OutsideControlData.ActivatedHornHigh" \
 "message.OutsideControlData.ActivatedHornLow" \
 "message.MessagePayload.ThreewaySwitchState"
```

### Windows (PowerShell)
```powershell
python analysis/src/plot_data_plotly.py data.jsonl `
 --field-paths "message.OutsideControlData.ActivatedHornHigh" `
 "message.OutsideControlData.ActivatedHornLow" `
 "message.MessagePayload.ThreewaySwitchState"
```

### Windows (cmd)
```cmd
python analysis/src/plot_data_plotly.py data.jsonl --field-paths "message.OutsideControlData.ActivatedHornHigh" "message.OutsideControlData.ActivatedHornLow" "message.MessagePayload.ThreewaySwitchState"
```

# Using simple field names (searches common locations)

### Unix/Linux/Mac
```bash
python analysis/src/plot_data_plotly.py data.jsonl \
 --fields ActivatedHornHigh ActivatedHornLow ThreewaySwitchState
```

### Windows (PowerShell)
```powershell
python analysis/src/plot_data_plotly.py data.jsonl `
 --fields ActivatedHornHigh ActivatedHornLow ThreewaySwitchState
```

### Windows (cmd)
```cmd
python analysis/src/plot_data_plotly.py data.jsonl --fields ActivatedHornHigh ActivatedHornLow ThreewaySwitchState
```

# Filter by message type

### Unix/Linux/Mac
```bash
python analysis/src/plot_data_plotly.py data.jsonl \
 --message-types "Remoot.SS139OutsideControlMessage" \
 --fields ActivatedHornHigh ActivatedHornLow
```

### Windows (PowerShell)
```powershell
python analysis/src/plot_data_plotly.py data.jsonl `
 --message-types "Remoot.SS139OutsideControlMessage" `
 --fields ActivatedHornHigh ActivatedHornLow
```

### Windows (cmd)
```cmd
python analysis/src/plot_data_plotly.py data.jsonl --message-types "Remoot.SS139OutsideControlMessage" --fields ActivatedHornHigh ActivatedHornLow
```

# Custom output directory and max points

### Unix/Linux/Mac
```bash
python analysis/src/plot_data_plotly.py data.jsonl \
 --fields ActivatedHornHigh ThreewaySwitchState \
 --max-points 5000 \
 --output-dir ./output
```

### Windows (PowerShell)
```powershell
python analysis/src/plot_data_plotly.py data.jsonl `
 --fields ActivatedHornHigh ThreewaySwitchState `
 --max-points 5000 `
 --output-dir ./output
```

### Windows (cmd)
```cmd
python analysis/src/plot_data_plotly.py data.jsonl --fields ActivatedHornHigh ThreewaySwitchState --max-points 5000 --output-dir ./output
```

# Skip PNG generation

### Unix/Linux/Mac
```bash
python analysis/src/plot_data_plotly.py data.jsonl \
 --fields ActivatedHornHigh \
 --no-png
```

### Windows (PowerShell)
```powershell
python analysis/src/plot_data_plotly.py data.jsonl `
 --fields ActivatedHornHigh `
 --no-png
```

### Windows (cmd)
```cmd
python analysis/src/plot_data_plotly.py data.jsonl --fields ActivatedHornHigh --no-png
```

# Specify encoding

### Unix/Linux/Mac
```bash
python analysis/src/plot_data_plotly.py data.jsonl \
 --fields ActivatedHornHigh \
 --encoding utf-16
```

### Windows (PowerShell)
```powershell
python analysis/src/plot_data_plotly.py data.jsonl `
 --fields ActivatedHornHigh `
 --encoding utf-16
```

### Windows (cmd)
```cmd
python analysis/src/plot_data_plotly.py data.jsonl --fields ActivatedHornHigh --encoding utf-16
```

## Example

### Unix/Linux/Mac

```bash
python analysis/src/plot_data_plotly.py data/couchdb_export_20260126_112255.jsonl \
 --field-paths "message.OutsideControlData.ActivateHornHigh" \
 "message.OutsideControlData.ActivateHornLow" \
 "message.MessagePayload.ThreewaySwitchState" \
 "message.SandingIsActive" \
 --max-points 3000 \
 --output-dir output
```

### Windows (PowerShell)

```powershell
python analysis/src/plot_data_plotly.py data/couchdb_export_20260126_112255.jsonl `
 --field-paths "message.OutsideControlData.ActivateHornHigh" `
 "message.OutsideControlData.ActivateHornLow" `
 "message.MessagePayload.ThreewaySwitchState" `
 "message.SandingIsActive" `
 --max-points 3000 `
 --output-dir output
```

### Windows (cmd)

```cmd
python analysis/src/plot_data_plotly.py data/couchdb_export_20260126_112255.jsonl --field-paths "message.OutsideControlData.ActivateHornHigh" "message.OutsideControlData.ActivateHornLow" "message.MessagePayload.ThreewaySwitchState" "message.SandingIsActive" --max-points 3000 --output-dir output
```
