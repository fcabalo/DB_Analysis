print("SCRIPT STARTED", flush=True)

import json
import csv
import os
import sys
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt

try:
    from dateutil.parser import isoparse  # type: ignore
except Exception:
    isoparse = None

#Default Values
DATA_PATH = "../data/"
SOURCE_FILE = "couchdb_export_20260126_112255.jsonl"
Y_PATH = "message.MessagePayload.SystemControlOverrideSwitchActivated"
TARGET_TYPE = "rse.ato.communication.ss139.extension.telegrams.RemoteTrainControlTelegram"
ON_CHANGE = False

TS_FIELD = "timestamp"
TYPE_FIELD = "messageContentType"

def parse_ts(s: str) -> datetime:
    # Robust für ISO 8601 inkl. +01:00
    if isoparse is not None:
        return isoparse(s)
    return datetime.fromisoformat(s)

def main(sourceFile, booleanFieldPath, messageContentType, onChangeOnly) -> None:
    xs = []
    ys = []

    total = 0
    matched = 0
    missing = 0
    
    previous = None
    pathList = booleanFieldPath.split(".")
    boolVar = pathList[-1]
    
    with open(DATA_PATH + sourceFile, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            total += 1
            obj = json.loads(line)
            if not isinstance(obj, dict):
                continue

            if obj.get(TYPE_FIELD) != messageContentType:
                continue

            matched += 1

            ts_raw = obj.get(TS_FIELD)
            y_val = obj
            for index in pathList:
                y_val = y_val.get(index) if isinstance(y_val, dict) else None
                #print(y_val)
            if ts_raw is None or y_val is None:
                missing += 1
                continue

            if onChangeOnly and previous is not None and previous == y_val:
                continue
            
            try:
                previous = y_val
                xs.append(parse_ts(str(ts_raw)))
                ys.append(bool(y_val))
            except Exception:
                missing += 1
                continue

            if matched % 50_000 == 0:
                print(f"Matched {matched:,} records (total read {total:,})...", flush=True)

    print("\n=== Summary ===")
    print(f"Total lines read: {total:,}")
    print(f"Matched type:     {matched:,}")
    print(f"Used for plot:    {len(xs):,}")
    print(f"Missing/invalid:  {missing:,}")

    if not xs:
        print("\nNo data points found to plot. Check field names and contentMessageType string.")
        return

    # Sort by time
    data = sorted(zip(xs, ys), key=lambda t: t[0])
    xs_sorted, ys_sorted = zip(*data)

    csv_out =  DATA_PATH + sourceFile.split(".")[0] + "_" + boolVar + ".csv"

    with open(csv_out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", boolVar])

        for ts, y in zip(xs, ys):
            writer.writerow([ts.isoformat(), y])

    print(f"CSV written to: {csv_out}")
    
    #Plotten des Graphen
    plt.figure()
    plt.step(xs_sorted, ys_sorted, where='post')
    plt.yticks([0, 1], ['False', 'True'])
    plt.xlabel("timestamp")
    plt.ylabel(boolVar)
    plt.title(TARGET_TYPE)
    plt.gcf().autofmt_xdate()  # x-axis labels readable
    plt.show()

if __name__ == "__main__":
    try:
        sourceFile = sys.argv[1]
    except IndexError:
        sourceFile = SOURCE_FILE

    try:
        booleanFieldPath = sys.argv[2]
    except IndexError:
        booleanFieldPath = Y_PATH

    try:
        messageContentType = sys.argv[3]
    except IndexError:
        messageContentType = TARGET_TYPE

    try:
        onChangeOnly = sys.argv[4]
    except IndexError:
        onChangeOnly = ON_CHANGE

    main(sourceFile, booleanFieldPath, messageContentType, bool(onChangeOnly))

