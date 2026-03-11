import pandas as pd
import matplotlib.pyplot as plt

# Load data
df = pd.read_csv("/workspaces/wildfire/data/us.wildfire.loss.csv")

# Create figure and primary axis
fig, ax1 = plt.subplots(figsize=(10,6))

# Secondary axis for percentfire
ax2 = ax1.twinx()

# Plot bars (percentfire) on right axis
ax2.bar(
    df["year"],
    df["percentfire"],
    color="moccasin",
    edgecolor="black",   # outline color
    linewidth=0.5,       # thin outline
    alpha=0.7,
    #label="Percent Fire",
    zorder=1
)

# Plot line (wildfireloss) on left axis
ax1.plot(
    df["year"],
    df["wildfireloss"],
    color="crimson",
    linewidth=4,
    #label="Wildfire Loss",
    zorder=3
)

# Axis labels
ax1.set_xlabel("Year", fontsize=16)
ax1.set_ylabel("Wildfire damages (billions $)", fontsize=16)
ax2.set_ylabel("Percent of total disaster losses", fontsize=16)

# Tick label size
ax1.tick_params(axis="both", labelsize=16)
ax2.tick_params(axis="both", labelsize=16)

# Ensure line appears above bars
ax1.set_zorder(ax2.get_zorder() + 1)
ax1.patch.set_visible(False)

# Optional grid
ax1.grid(True, axis="y", linestyle="--", alpha=0.5)

# Layout
#plt.title("Wildfire Loss and Percent of Total Disaster Losses")
plt.tight_layout()
plt.savefig("WildfireLoss.png", dpi=300, bbox_inches="tight")

plt.show()