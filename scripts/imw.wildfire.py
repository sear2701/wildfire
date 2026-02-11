import pandas as pd
import matplotlib.pyplot as plt

# --- Load data ---
# Update filename if needed
df = pd.read_csv("/workspaces/wildfire/data/imw.wildfire.csv")

# --- Column names (edit these to match your CSV) ---
year_col = "Year"
col_co = "Colorado"
col_ut = "Utah"
col_wy = "Wyoming"
col_imw = "Intermountain West"   # or "IntermountainWest"

# --- Make figure with 4 subpanels (2x2) ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

# Top-left: Colorado
axs[0, 0].plot(df[year_col], df[col_co], marker="o")
axs[0, 0].set_title("Colorado")
axs[0, 0].set_ylabel("Area burned (acres)")

# Top-right: Utah
axs[0, 1].plot(df[year_col], df[col_ut], marker="o")
axs[0, 1].set_title("Utah")

# Bottom-left: Wyoming
axs[1, 0].plot(df[year_col], df[col_wy], marker="o")
axs[1, 0].set_title("Wyoming")
axs[1, 0].set_xlabel("Year")
axs[1, 0].set_ylabel("Area burned (acres)")

# Bottom-right: Intermountain West
axs[1, 1].plot(df[year_col], df[col_imw], marker="o")
axs[1, 1].set_title("Intermountain West")
axs[1, 1].set_xlabel("Year")

# --- Formatting ---
for ax in axs.ravel():
    ax.grid(True, alpha=0.3)
    
# --- Save to PNG ---
out_png = "wildfire_area_burned_4panel.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")

plt.tight_layout()
plt.show()
