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
def summarize(data, label, spike_threshold_ms=5):
    summary = []
    for name, durations in data.items():
        total = sum(durations)
        avg = total / len(durations)
        count = len(durations)
        max_dur = max(durations)
        min_dur = min(durations)
        resource = extract_resource(name)
        over_threshold = sum(1 for d in durations if d / 1000 > spike_threshold_ms)
        freq_per_sec = count / (max(durations) / 1_000_000) if durations else 0
        summary.append((
            name,
            avg / 1000,                # average in ms
            count,
            total / 1000,              # total in ms
            resource,
            freq_per_sec,
            max_dur / 1000,            # max in ms
            min_dur / 1000,            # min in ms
            over_threshold             # how many above threshold
        ))
    return sorted(summary, key=lambda x: x[1], reverse=True)


tick_summary = summarize(categories["tick"], "tick")
ref_summary = summarize(categories["ref_call"], "ref_call")
event_summary = summarize(categories["event"], "event")

# Grouped by resource
resource_ranking = sorted(resource_totals.items(), key=lambda x: x[1], reverse=True)

# Plot helper
def plot_top10(data, title, filename):
    names = [row[0][:40] + "..." if len(row[0]) > 40 else row[0] for row in data[:10]]
    values = [row[1] for row in data[:10]]  # avg time (ms)
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

# Helper to render detailed tables with top N rows
def add_table(pdf, title, summary_data, total_cpu):
    pdf.add_page()
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, title, ln=True)
    pdf.set_font("Arial", "B", 8)
    headers = ["Function", "Avg (ms)", "Max (ms)", "Min (ms)", "Total (ms)", "Calls", "% Total", "Freq/s", ">5ms"]
    col_widths = [50, 16, 16, 16, 20, 18, 20, 18, 16]

    for i, h in enumerate(headers):
        pdf.cell(col_widths[i], 6, h, border=1)
    pdf.ln()

    pdf.set_font("Arial", size=7)
    for row in summary_data[:20]:
        name, avg, count, total, resource, freq, max_d, min_d, spikes = row
        percent = (total / total_cpu) * 100 if total_cpu > 0 else 0
        cells = [
            name[:48] + "..." if len(name) > 48 else name,
            f"{avg:.2f}", f"{max_d:.2f}", f"{min_d:.2f}", f"{total:.1f}",
            str(count), f"{percent:.1f}%", f"{freq:.2f}", str(spikes)
        ]
        for i, text in enumerate(cells):
            pdf.cell(col_widths[i], 6, text, border=1)
        pdf.ln()


# Total CPU time for % calculations
total_cpu_time = sum(resource_totals.values())


# Save final PDF

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

# Add detailed tables to the PDF
add_table(pdf, "Top Tick Handlers (Detailed)", tick_summary, total_cpu_time)
add_table(pdf, "Top Lua Ref Calls (Detailed)", ref_summary, total_cpu_time)
add_table(pdf, "Top Custom Events (Detailed)", event_summary, total_cpu_time)


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
