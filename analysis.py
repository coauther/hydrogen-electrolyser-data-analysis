import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

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


# Select the experimental variables
current = df["current_A"]
voltage = df["voltage_V"]

# Fit a first-order polynomial: U = R * I + U0
slope, intercept = np.polyfit(current, voltage, 1)

# Calculate the voltage predicted by the model
df["predicted_voltage_V"] = slope * current + intercept

# Calculate residuals
df["voltage_residual_V"] = (
    voltage - df["predicted_voltage_V"]
)

# Calculate the residual sum of squares
ss_res = np.sum(df["voltage_residual_V"] ** 2)

# Calculate the total sum of squares
ss_tot = np.sum((voltage - voltage.mean()) ** 2)

# Coefficient of determination
r_squared = 1 - ss_res / ss_tot

print("\nLinear Regression Results")
print("-------------------------")
print(f"Effective resistance: {slope:.4f} ohm")
print(f"Voltage intercept: {intercept:.4f} V")
print(f"R-squared: {r_squared:.4f}")
print(
    f"Fitted equation: "
    f"U = {slope:.4f}I + {intercept:.4f}"
)

print(
    df[
        [
            "current_A",
            "voltage_V",
            "predicted_voltage_V",
            "voltage_residual_V",
        ]
    ].round(4)
)

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

# plt.savefig(FIGURE_DIR / "UI_curve.png", dpi=300, bbox_inches="tight")
# plt.show()


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

# plt.savefig(FIGURE_DIR / "PI_curve.png", dpi=300, bbox_inches="tight")
# plt.show()


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

# plt.savefig(FIGURE_DIR / "Efficiency_Current_Curve.png", dpi=300, bbox_inches="tight")
# plt.show()

# Generate a smooth current range for the fitted line
fit_current = np.linspace(
    current.min(),
    current.max(),
    100
)

fit_voltage = slope * fit_current + intercept

plt.figure(figsize=(8, 6))

plt.scatter(
    current,
    voltage,
    color="royalblue",
    label="Measured data",
    zorder=3
)

plt.plot(
    fit_current,
    fit_voltage,
    color="darkorange",
    linewidth=2,
    label="Linear regression"
)

plt.xlabel("Current (A)")
plt.ylabel("Voltage (V)")
plt.title("Electrolyser Voltage–Current Linear Regression")
plt.grid(True, alpha=0.3)
plt.legend()

# Display the equation inside the graph
equation_text = (
    f"U = {slope:.4f}I + {intercept:.4f}\n"
    f"$R^2$ = {r_squared:.4f}"
)

plt.text(
    0.05,
    0.95,
    equation_text,
    transform=plt.gca().transAxes,
    verticalalignment="top",
    bbox={
        "boxstyle": "round",
        "facecolor": "white",
        "alpha": 0.8,
    }
)

plt.tight_layout()
plt.savefig(
FIGURE_DIR /
    "voltage_current_regression.png",
    dpi=300,
    bbox_inches="tight"
)

plt.figure(figsize=(8, 5))

plt.scatter(
    current,
    df["voltage_residual_V"],
    color="seagreen",
    zorder=3
)

plt.axhline(
    y=0,
    color="black",
    linestyle="--",
    linewidth=1
)

plt.xlabel("Current (A)")
plt.ylabel("Voltage Residual (V)")
plt.title("Residual Analysis of the Linear Model")
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(
FIGURE_DIR /
    "voltage_residuals.png",
    dpi=300,
    bbox_inches="tight"
)
plt.show()