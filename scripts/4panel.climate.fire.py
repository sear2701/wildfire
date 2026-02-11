import csv
import matplotlib.pyplot as plt

# ---- Load data (no pandas needed) ----
years, avtemp, avprecip, pdsi, macres = [], [], [], [], []

with open("/workspaces/wildfire/data/west.fire.climate.csv", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        y = int(row["year"])

        # Climate series: keep 1983–2025
        if 1983 <= y <= 2025:
            years.append(y)
            avtemp.append(float(row["avtemp"]))
            avprecip.append(float(row["avprecip"]))
            pdsi.append(float(row["pdsi"]))

            # Fire series: keep only if present (we'll subset to 1983–2024 later)
            macres.append(float(row["macres"]) if row["macres"] != "" else None)

# Sort by year (just in case the CSV isn't ordered)
data = sorted(zip(years, avtemp, avprecip, pdsi, macres), key=lambda x: x[0])
years, avtemp, avprecip, pdsi, macres = map(list, zip(*data))

# ---- Build 4-panel figure ----
fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=False)

# Top-left: Temperature (1895–2024)
ax = axes[0, 0]
ax.plot(years, avtemp, marker="o", linewidth=1.5, color="black", markersize=3)
ax.text(0.5, 0.98, "Temperature", transform=ax.transAxes,
        ha="center", va="top", fontsize=15, fontweight="bold")
ax.set_xlim(1980, 2028)
ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("Average temperature (°F)", fontsize=13)

# Top-right: Precipitation (1895–2024)
ax = axes[0, 1]
ax.plot(years, avprecip, marker="o", linewidth=1.5, color="black", markersize=3)
ax.text(0.5, 0.98, "Precipitation", transform=ax.transAxes,
        ha="center", va="top", fontsize=15, fontweight="bold")
ax.set_xlim(1980, 2028)
ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("Precipitation (in)", fontsize=13)

# Bottom-left: Drought (PDSI) (1895–2024)
ax = axes[1, 0]
pdsi_colors = ["green" if v >= 0 else "saddlebrown" for v in pdsi]
ax.bar(years, pdsi, color=pdsi_colors, edgecolor="black", linewidth=0.5)
ax.axhline(0, color="black", linewidth=1)
ax.text(0.5, 0.98, "Drought (PDSI)", transform=ax.transAxes,
        ha="center", va="top", fontsize=15, fontweight="bold")
ax.set_xlim(1980, 2028)
ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("PDSI", fontsize=13)

# Bottom-right: Wildfire area burned (keep 1983–2024 only)
ax = axes[1, 1]
years_m = [y for y, m in zip(years, macres) if (m is not None) and (1983 <= y <= 2025)]
macres_m = [m for y, m in zip(years, macres) if (m is not None) and (1983 <= y <= 2025)]

ax.bar(years_m, macres_m, color="gray", edgecolor="black", linewidth=0.5)
ax.set_xlim(1982, 2025)
ax.text(0.45, 0.98, "Wildfire", transform=ax.transAxes,
        ha="center", va="top", fontsize=15, fontweight="bold")
ax.set_xlabel("Year", fontsize=13)
ax.set_ylabel("Burned area (millions of acres)", fontsize=13)

plt.tight_layout()
plt.savefig("four_panel_climate_fire.png", dpi=300, bbox_inches="tight")
plt.show()
