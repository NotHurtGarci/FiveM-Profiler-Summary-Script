# FiveM Profiler Summary Script
This is a Python script to analyze FiveM profiler JSON exports, identify high-CPU scripts, generate performance charts, and produce a simple PDF report.

I created this to analyze faster the profiler files with a lot of things going on at the same time, just to have a better visual view.
This is something easy but I wanted to leave it here in case I need it and maybe I add more scripts or useful things in the future to check optimization of your FiveM server.

---

## 🚀 Features

- Parses FiveM profiler `.json` trace files.
- Identifies the most CPU-expensive:
  - `tick()` handlers
  - `ref call` Lua function executions
  - `event:` custom events
- Calculates:
  - Average execution time
  - Execution frequency
  - Total accumulated CPU time
- Groups and ranks resource usage by script name.
- Detects high-frequency executions (e.g., running on every tick).
- Generates visual charts for top offenders.

---

## 📊 Output

- **PNG charts** showing top:
  - Tick handlers
  - Ref calls
  - Events
- **Console output** listing:
  - Top-performing scripts by average time
  - Total CPU time consumed per resource
- **PDF report** with all included.


---

## 🧰 Requirements

- Python 3.7+
- Required packages:

```bash
pip install matplotlib fpdf

