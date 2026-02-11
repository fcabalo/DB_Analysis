print("SCRIPT STARTED", flush=True)

import json
import csv
import os
import sys
import threading
from pathlib import Path
from datetime import datetime

import matplotlib.pyplot as plt

try:
    from dateutil.parser import isoparse  # type: ignore
except Exception:
    isoparse = None

#Default Values
DATA_PATH = "../data/"
CONFIG_FILE = "config.json"

TS_FIELD = "timestamp"
TYPE_FIELD = "messageContentType"

#All fields needed to create the plot
class PlotData:
    def __init__(self, axis, index):
        self.index = index
        self.datatype = axis["datatype"]
        self.fieldPath = axis["fieldPath"]
        self.onChangeOnly = axis["onChangeOnly"] if "onChangeOnly" in axis and axis["onChangeOnly"] else False
        self.datetimeFrom = parse_ts(axis["datetimeFrom"]) if "datetimeFrom" in axis and axis["datetimeFrom"] else None
        self.datetimeTo = parse_ts(axis["datetimeTo"]) if "datetimeTo" in axis and axis["datetimeTo"] else None
        self.ylabel = axis["ylabel"] if "ylabel" in axis and axis["ylabel"] else self.fieldPath.split(".")[-1]
        self.plotType = axis["plotType"] if "plotType" in axis and axis["plotType"] else "plot"
        self.style = axis["style"] if "style" in axis and axis["style"] else "-b"
        self.title = axis["title"] if "title" in axis and axis["title"] else None
        self.sourceFile = axis["sourceFile"]
        self.messageContentType = axis["messageContentType"]
        self.csvFileName = axis["csvFileName"].split(".")[0] if "csvFileName" in axis and axis["csvFileName"] else None
        self.data = {"x": [], "y": []}

def parse_ts(s: str) -> datetime:
    if isoparse is not None:
        return isoparse(s)
    return datetime.fromisoformat(s)

def main(config) -> None:
    subplots = load_and_validate_config(config)
    
    
    threads = []
    
    for subplot in subplots:
        t = threading.Thread(target=extract_data, args=(subplot,))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()
        
    plot(subplots, config)

#Extract the data from source file     
def extract_data(subplot):
    xs = []
    ys = []
    
    total = 0
    matched = 0
    missing = 0
    
    previous = None
    pathList = subplot.fieldPath.split(".")
    
    print(f"[{subplot.index}]Extracting {pathList[-1]} Data from {subplot.sourceFile}")
    with open(DATA_PATH + subplot.sourceFile, "r", encoding="utf-8-sig") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            total += 1
            obj = json.loads(line)
            if not isinstance(obj, dict):
                continue

            if obj.get(TYPE_FIELD) != subplot.messageContentType:
                continue

            matched += 1

            ts_raw = obj.get(TS_FIELD)
            y_val = obj
            for index in pathList:
                y_val = y_val.get(index) if isinstance(y_val, dict) else None
                
            if ts_raw is None or y_val is None:
                missing += 1
                continue

            if subplot.onChangeOnly and previous is not None and previous == y_val:
                continue
            
            dt = parse_ts(str(ts_raw))
            
            if subplot.datetimeFrom and dt < subplot.datetimeFrom:
                continue
                
            if subplot.datetimeTo and dt > subplot.datetimeTo:
                continue
            
            try:
                previous = y_val
                xs.append(dt)
                ys.append(y_val)
            except Exception:
                missing += 1
                continue

            if matched % 50_000 == 0:
                print(f"[{subplot.index}]Matched {matched:,} records (total read {total:,})...", flush=True)

    print("\n=== Summary ===")
    print(f"[{subplot.index}]Total lines read: {total:,}")
    print(f"[{subplot.index}]Matched type:     {matched:,}")
    print(f"[{subplot.index}]Used for plot:    {len(xs):,}")
    print(f"[{subplot.index}]Missing/invalid:  {missing:,}")

    if not xs:
        print("\n[{subplot.index}]No data points found to plot. Check field names and contentMessageType string.")
        return

    data = sorted(zip(xs, ys), key=lambda t: t[0])
    xs_sorted, ys_sorted = zip(*data)

    subplot.data["x"] = xs_sorted
    subplot.data["y"] = ys_sorted
    
    if subplot.csvFileName:
        header = ["timestamp", pathList[-1]]
        write_to_csv(DATA_PATH + subplot.csvFileName + ".csv", data, header)
    
def write_to_csv(filename, data, header):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for ts, y in data:
            writer.writerow([ts.isoformat(), y])
            
        print(f"CSV written to: {filename}")
    
#Plot the data based on config
def plot(subplots, config):
    print("Plotting Data")
    fig, axes = plt.subplots(config["rows"], config["columns"])
    if "title" in config and config["title"]:
        fig.suptitle(config["title"] )
    
    col = 0
    row = 0
    index = 0
    
    for subplot in subplots:
        
        if config["columns"] == 1:
            axis = axes[row]
        elif config["rows"] == 1:
            axis = axes[col]
        else:
            axis = axes[row, col]
        
        if subplot.datatype == "boolean":
            axis.step('x', 'y', subplot.style, where='post', data=subplot.data)
            axis.set_yticks([0, 1], ['False', 'True'])
        elif subplot.plotType == "step":
            axis.step('x', 'y', subplot.style, where='post', data=subplot.data)
        else:
            axis.plot('x', 'y', subplot.style, data=subplot.data)
            
        axis.set_ylabel(subplot.ylabel)
        
        if subplot.title:
            axis.set_title(subplot.title)
        
        index += 1
        col += 1
        
        if col == config["columns"]: #row full, plot on next
            row += 1
            col = 0
    
    plt.xlabel(config["xlabel"] if "xlabel" in config and config["xlabel"] else "Timestamp")
    plt.gcf().autofmt_xdate()
    plt.show()

#Load config file
def configure(configFile) -> {}:
    try:
        with open(DATA_PATH + configFile, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"config file not found: {configFile}")
    except PermissionError:
        print(f"Permission denied accessing config file: {configFile}")
    except Exception as e:
        print(f"Unexpected error loading config: {e}")

#Validate config file for required fields and load each axes dictionary to PlotData
def load_and_validate_config(config):
    plotCount = 0
    
    try:
        plotCount = config["rows"] * config["columns"]
    except KeyError:
        print("rows and columns fields are mandatory.") 
        sys.exit()
        
    if plotCount < len(config["axes"]):
        print(f"Axes details count({len(config["axes"])}) is > rows * columns({plotCount})")
        sys.exit()
    
    plots = []
    index = 0    
    for axis in config["axes"]:
        plot = PlotData(axis, index)
        if plot.sourceFile is None or plot.messageContentType is None:
            print(f"Axes[{index}]: sourceFile and messageContentType must be present for each axis")
            sys.exit()
        index += 1
        plots.append(plot)
        
    return plots

if __name__ == "__main__":
    try:
        configFile = sys.argv[1]
    except IndexError:
        configFile = CONFIG_FILE
    
    main(configure(configFile))

