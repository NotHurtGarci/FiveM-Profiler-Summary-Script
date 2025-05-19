import json
from collections import defaultdict
import matplotlib.pyplot as plt
from fpdf import FPDF

# Path to profiler JSON file
PROFILE_FILE = "profile.json" # Change this to your file name

# Load the JSON data
with open(PROFILE_FILE, "r", encoding="utf-8") as f:
    events = json.load(f)

# Categorize events
categories = {
    "tick": defaultdict(list),
    "ref_call": defaultdict(list),
    "event": defaultdict(list)
}
timestamps = {}
resource_totals = defaultdict(float)
resource_counts = defaultdict(int)

def classify_event(name):
    if name.startswith("tick ("):
        return "tick"
    elif name.startswith("ref call"):
        return "ref_call"
    elif name.startswith("event:"):
        return "event"
    return None

def extract_resource(name):
    if " (" in name:
        return name.split(" (")[-1].rstrip(")")
    if "@" in name:
        return name.split("@")[-1].split("/")[0]
    return name.split(":")[0]

# Parse all events and calculate durations
for event in events:
    name = event.get("name")
    ts = event.get("ts")
    ph = event.get("ph")
    kind = classify_event(name)
    if kind and name and ts is not None:
        if ph == "B":
            timestamps[name] = ts
        elif ph == "E" and name in timestamps:
            duration = ts - timestamps[name]
            categories[kind][name].append(duration)
            resource = extract_resource(name)
            resource_totals[resource] += duration / 1000  # to ms
            resource_counts[resource] += 1
            del timestamps[name]

# Analyze grouped data
def summarize(data, label):
    summary = []
    for name, durations in data.items():
        total = sum(durations)
        avg = total / len(durations)
        count = len(durations)
        resource = extract_resource(name)
        freq_per_sec = count / (max(durations) / 1_000_000) if durations else 0
        summary.append((name, avg / 1000, count, total / 1000, resource, freq_per_sec))
    return sorted(summary, key=lambda x: x[1], reverse=True)

tick_summary = summarize(categories["tick"], "tick")
ref_summary = summarize(categories["ref_call"], "ref_call")
event_summary = summarize(categories["event"], "event")

# Grouped by resource
resource_ranking = sorted(resource_totals.items(), key=lambda x: x[1], reverse=True)

# Plot helper
def plot_top10(data, title, filename):
    names = [n[:40] + "..." if len(n) > 40 else n for n, _, _, _, _, _ in data[:10]]
    values = [v for _, v, _, _, _, _ in data[:10]]
    plt.figure(figsize=(10, 5))
    plt.barh(names, values, color='skyblue')
    plt.xlabel("Average Execution Time (ms)")
    plt.title(title)
    plt.gca().invert_yaxis()
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Generate charts
plot_top10(tick_summary, "Top 10 Tick Handlers", "chart_ticks.png")
plot_top10(ref_summary, "Top 10 Ref Calls", "chart_refcalls.png")
plot_top10(event_summary, "Top 10 Events", "chart_events.png")


# Generate PDF report
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", "B", 16)
pdf.cell(200, 10, "FiveM Server Optimization Report", ln=True, align="C")
pdf.ln(10)

pdf.set_font("Arial", "B", 12)
pdf.cell(200, 10, "Executive Summary", ln=True)
pdf.set_font("Arial", size=11)
pdf.multi_cell(0, 8, """This report summarizes profiler analysis for the FiveM server. It highlights scripts and events with the highest CPU cost and frequency, with visual charts and actionable insights.""")

# Insert charts
for title, path in [("Tick Handlers", "chart_ticks.png"),
                    ("Lua Ref Calls", "chart_refcalls.png"),
                    ("Custom Events", "chart_events.png")]:
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, f"{title}", ln=True)
    pdf.image(path, x=10, y=30, w=190)


# Resource table
pdf.add_page()
pdf.set_font("Arial", "B", 14)
pdf.cell(200, 10, "Top Resources by Total CPU Time", ln=True)
pdf.set_font("Arial", size=11)
for res, total in resource_ranking[:15]:
    pdf.cell(0, 8, f"- {res}: {total:.2f} ms total", ln=True)

pdf.output("FiveM_Optimization_Report.pdf")



print("✅ Analysis complete.")
print("Charts saved: chart_ticks.png, chart_refcalls.png, chart_events.png")
print("✅ PDF report generated: FiveM_Optimization_Report.pdf")
print("\n🔍 Top 5 Resource Consumers:")
for name, total in resource_ranking[:5]:
    print(f"- {name}: {total:.2f} ms total CPU time")
