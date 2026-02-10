# Using field paths (recommended - most explicit)

```bash
python process_telemetry.py data.jsonl \
 --field-paths "message.OutsideControlData.ActivatedHornHigh" \
 "message.OutsideControlData.ActivatedHornLow" \
 "message.MessagePayload.ThreewaySwitchState"
```

# Using simple field names (searches common locations)

```bash
python process_telemetry.py data.jsonl \
 --fields ActivatedHornHigh ActivatedHornLow ThreewaySwitchState
```

# Filter by message type

```bash
python process_telemetry.py data.jsonl \
 --message-types "Remoot.SS139OutsideControlMessage" \
 --fields ActivatedHornHigh ActivatedHornLow
```

# Custom output directory and max points

```bash
python process_telemetry.py data.jsonl \
 --fields ActivatedHornHigh ThreewaySwitchState \
 --max-points 5000 \
 --output-dir ./output
```

# Skip PNG generation

```bash
python process_telemetry.py data.jsonl \
 --fields ActivatedHornHigh \
 --no-png
```

# Specify encoding

```bash
python process_telemetry.py data.jsonl \
 --fields ActivatedHornHigh \
 --encoding utf-16
```

## Example

### Unix/Linux/Mac

```bash
python process_telemetry.py ../data/couchdb_export_20260126_112255.jsonl \
 --field-paths "message.OutsideControlData.ActivateHornHigh" \
 "message.OutsideControlData.ActivateHornLow" \
 "message.MessagePayload.ThreewaySwitchState" \
 "message.SandingIsActive" \
 --max-points 3000 \
 --output-dir ../output
```

### Windows (PowerShell)

```powershell
python process_telemetry.py ../data/couchdb_export_20260126_112255.jsonl `
 --field-paths "message.OutsideControlData.ActivateHornHigh" `
 "message.OutsideControlData.ActivateHornLow" `
 "message.MessagePayload.ThreewaySwitchState" `
 "message.SandingIsActive" `
 --max-points 3000 `
 --output-dir ../output
```

### Windows (cmd) or single line

```cmd
python process_telemetry.py ../data/couchdb_export_20260126_112255.jsonl --field-paths "message.OutsideControlData.ActivateHornHigh" "message.OutsideControlData.ActivateHornLow" "message.MessagePayload.ThreewaySwitchState" "message.SandingIsActive" --max-points 3000 --output-dir ../output
```
