import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

df = pd.read_csv("data/processed/capacity_thresholds.csv")
df = df.sort_values("retained_capacity")

ax= df.plot(
    x="retained_capacity",
    y=["threshold_without_rival", "threshold_with_rival"],
)

ax.set_xlabel("Retained human capacity (K)")
ax.set_ylabel("AI price multiplier at switching")
ax.legend(["Without rival", "With rival"])
ax.set_title("Hypothetical scenario")

Path("figures").mkdir(exist_ok=True)
plt.savefig("figures/capacity_thresholds.png", dpi=300, bbox_inches="tight")
plt.show()
