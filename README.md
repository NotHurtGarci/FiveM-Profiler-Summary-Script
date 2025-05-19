# FiveM Profiler Summary Script

This is a Python script to analyze FiveM profiler JSON exports, identify high-CPU scripts, generate performance charts, and produce a detailed PDF report.

I created this to analyze profiler files faster, especially when there's a lot going on in the server. It gives a much better visual and statistical view of what's consuming CPU, and can help identify optimization targets. I may keep adding more features in the future for server performance analysis.

---

## 🚀 Features

- Parses FiveM profiler `.json` trace files.
- Identifies the most CPU-expensive:
  - `tick()` handlers
  - `ref call` Lua function executions
  - `event:` custom events
- Calculates for each function:
  - Average execution time (ms)
  - Total accumulated CPU time (ms)
  - Max and min execution time (peak detection)
  - Execution frequency (calls per second)
  - Count of executions over a 5ms threshold
- Groups and ranks total CPU usage by resource.
- Detects high-frequency executions (e.g., running every tick).
- Generates PNG charts for quick overview.
- Generates a PDF report with:
  - Charts
  - Detailed tables with spikes, percentages, and metrics

---

## 📊 Output

- **PNG charts** showing:
  - Top 10 tick handlers
  - Top 10 Lua ref calls
  - Top 10 events
- **Console output** listing:
  - Top 5 resource consumers by total CPU time
- **PDF report**:
  - Summary with charts
  - Extended tables with:
    - Function name
    - Average, max, min time
    - Total executions
    - % of total CPU time
    - Frequency per second
    - Spike count (>5ms)

---

## 🧰 Requirements

- Python 3.7+
- Required packages:

```bash
pip install matplotlib fpdf
