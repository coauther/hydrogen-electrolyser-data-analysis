import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# Define project folders
DATA_DIR = Path("data")
FIGURE_DIR = Path("figures")

RAW_DATA_PATH = DATA_DIR / "electrolyser_data.csv"
PROCESSED_DATA_PATH = DATA_DIR / "electrolyser_processed.csv"


def annotate_points(x_data, y_data, unit="", decimals=2, x_offsets=None, y_offsets=None):
    """
    Add value labels to each data point in a matplotlib plot.

    Parameters:
        x_data: pandas Series used as x-axis data
        y_data: pandas Series used as y-axis data
        unit: text unit added after the value, e.g. " V", " W", " %"
        decimals: number of decimal places shown in the label
        x_offsets: optional list for horizontal label adjustment
        y_offsets: optional list for vertical label adjustment
    """

    n = len(x_data)

    # If no offsets are provided, use zero offset for all labels
    if x_offsets is None:
        x_offsets = [0] * n

    if y_offsets is None:
        y_offsets = [0] * n

    # Add text label for each point
    for i in range(n):
        x = x_data.iloc[i]
        y = y_data.iloc[i]
        label = f"{y:.{decimals}f}{unit}"

        plt.text(
            x + x_offsets[i],
            y + y_offsets[i],
            label
        )


# Read raw experimental data
df = pd.read_csv(RAW_DATA_PATH)


# Calculate engineering parameters
df["power_W"] = df["voltage_V"] * df["current_A"]
df["electrical_energy_J"] = df["power_W"] * df["time_s"]
df["efficiency_percent"] = df["hydrogen_energy_J"] / df["electrical_energy_J"] * 100


# Save processed data with full precision
df.to_csv(PROCESSED_DATA_PATH, index=False)


# Create a rounded copy only for terminal display
display_df = df.copy()
display_df["power_W"] = display_df["power_W"].round(3)
display_df["electrical_energy_J"] = display_df["electrical_energy_J"].round(2)
display_df["efficiency_percent"] = display_df["efficiency_percent"].round(1)

print(display_df)


# -----------------------------
# Plot 1: U-I characteristic curve
# -----------------------------

plt.figure()
plt.plot(df["current_A"], df["voltage_V"], marker="o")

plt.xlabel("Current (A)")
plt.ylabel("Voltage (V)")
plt.title("U-I Characteristic Curve of Electrolyser")
plt.grid(True)

annotate_points(
    df["current_A"],
    df["voltage_V"],
    unit=" V",
    decimals=2,
    x_offsets=[-0.04, -0.05, -0.05, -0.03],
    y_offsets=[-0.02, 0.01, 0.01, 0]
)

plt.savefig(FIGURE_DIR / "UI_curve.png", dpi=300, bbox_inches="tight")
plt.show()


# -----------------------------
# Plot 2: Power-current curve
# -----------------------------

plt.figure()
plt.plot(df["current_A"], df["power_W"], marker="o")

plt.xlabel("Current (A)")
plt.ylabel("Power (W)")
plt.title("Power-Current Curve of Electrolyser")
plt.grid(True)

annotate_points(
    df["current_A"],
    df["power_W"],
    unit=" W",
    decimals=2,
    x_offsets=[0.02, 0.02, 0.02, -0.10],
    y_offsets=[0.01, 0.02, 0.02, 0.03]
)

plt.savefig(FIGURE_DIR / "PI_curve.png", dpi=300, bbox_inches="tight")
plt.show()


# -----------------------------
# Plot 3: Efficiency-current curve
# -----------------------------

plt.figure()
plt.plot(df["current_A"], df["efficiency_percent"], marker="o")

plt.xlabel("Current (A)")
plt.ylabel("Efficiency (%)")
plt.title("Efficiency-Current Curve of Electrolyser")
plt.ylim(50, 80)
plt.grid(True)

annotate_points(
    df["current_A"],
    df["efficiency_percent"],
    unit=" %",
    decimals=1,
    x_offsets=[0.01, 0.01, 0.01, -0.06],
    y_offsets=[0.10, 0.12, 0.35, 0.30]
)

plt.savefig(FIGURE_DIR / "Efficiency_Current_Curve.png", dpi=300, bbox_inches="tight")
plt.show()