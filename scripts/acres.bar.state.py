import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("/workspaces/wildfire/data/imw.wildfire.csv")

# Create the bar graph
plt.figure()
plt.bar(
    df["Year"],
    df["Utah"],
    color="darkgray",
    edgecolor="black",
    linewidth=0.8
)

# Labels
plt.xlabel("Year")
plt.ylabel("Burned area (acres)")

# Save and show
plt.savefig("burned_area_year_utah.png", dpi=300, bbox_inches="tight")
plt.show()

