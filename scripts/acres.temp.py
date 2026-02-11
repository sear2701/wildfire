import csv
import matplotlib.pyplot as plt

years = []
macres = []
avtemp = []

# Read data from CSV
with open("/workspaces/wildfire/data/west.fire.climate.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        years.append(int(row["year"]))
        macres.append(float(row["macres"]))
        avtemp.append(float(row["avtemp"]))

# Create figure and first axis (macres)
fig, ax1 = plt.subplots()

ax1.bar(
    years,
    macres,
    color="darkgray",
    edgecolor="black",
    linewidth=0.8
)
ax1.set_xlabel("Year")
ax1.set_ylabel("Burned area (millions of acres)")

# Create second y-axis (avtemp)
ax2 = ax1.twinx()
ax2.plot(
    years,
    avtemp,
    color="black",
    marker="o",
    markerfacecolor="black",
    markeredgecolor="black",
    linewidth=1.5
)
ax2.set_ylabel("Average temperature")

# Title
plt.title("Macres and Average Temperature by Year")

# Save figure
plt.savefig("macres_avtemp_dual_axis.png", dpi=300, bbox_inches="tight")
plt.close()
