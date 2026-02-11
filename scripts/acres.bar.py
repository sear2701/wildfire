import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv("/workspaces/wildfire/data/west.fire.climate.csv")

# Create the bar graph
plt.figure()
plt.bar(
    df["year"],
    df["macres"],
    color="darkgray",
    edgecolor="black",
    linewidth=0.8
)

# Labels
plt.xlabel("Year")
plt.ylabel("Burned area (millions of acres)")

# Save and show
plt.savefig("burned_area_year.png", dpi=300, bbox_inches="tight")
plt.show()

