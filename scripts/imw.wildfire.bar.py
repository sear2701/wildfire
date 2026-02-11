import pandas as pd
import matplotlib.pyplot as plt

# --- Load data ---
df = pd.read_csv("/workspaces/wildfire/data/imw.wildfire.kacres.csv")

# --- Column names (edit these to match your CSV) ---
year_col = "Year"
col_co = "Colorado"
col_ut = "Utah"
col_wy = "Wyoming"
col_imw = "Intermountain West"  # or "IntermountainWest"

# --- Helper: make colors so year==2025 is red ---
def colors_for_2025(years, default_color="steelblue", highlight_color="red"):
    return [highlight_color if int(y) == 2025 else default_color for y in years]

# --- Make figure with 4 subpanels (2x2) ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8), sharex=True)

# Top-left: Colorado
axs[0, 0].bar(df[year_col], df[col_co], color=colors_for_2025(df[year_col]))
axs[0, 0].set_title("Colorado")
axs[0, 0].set_ylabel("Area burned (1000s of acres)")

# Top-right: Utah
axs[0, 1].bar(df[year_col], df[col_ut], color=colors_for_2025(df[year_col]))
axs[0, 1].set_title("Utah")

# Bottom-left: Wyoming
axs[1, 0].bar(df[year_col], df[col_wy], color=colors_for_2025(df[year_col]))
axs[1, 0].set_title("Wyoming")
axs[1, 0].set_xlabel("Year")
axs[1, 0].set_ylabel("Area burned (1000s of acres)")

# Bottom-right: Intermountain West
axs[1, 1].bar(df[year_col], df[col_imw], color=colors_for_2025(df[year_col]))
axs[1, 1].set_title("Intermountain West")
axs[1, 1].set_xlabel("Year")

# --- Formatting ---
for ax in axs[0, :]:        # top row
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, 850)

for ax in axs[1, :]:        # bottom row
    ax.grid(True, axis="y", alpha=0.3)
    ax.set_ylim(0, 1825)

plt.tight_layout()

# --- Save to PNG ---
out_png = "wildfire_area_burned_4panel_bar_highlight2025.png"
plt.savefig(out_png, dpi=300, bbox_inches="tight")

plt.show()
