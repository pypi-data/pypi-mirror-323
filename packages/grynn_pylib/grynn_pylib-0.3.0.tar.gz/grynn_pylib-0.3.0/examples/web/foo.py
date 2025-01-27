# CAGR 2

# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from matplotlib.widgets import Button
import json

# %%

# Plot drawdowns, over 10 years, for XLK, NIFTYBEES(USD), SPY

# Download data
df = yf.download("XLK, SPY, NIFTYBEES.NS", period="10y")["Adj Close"]

# Clean data errors
df.loc["2019-12-19":"2019-12-20", "NIFTYBEES.NS"] = np.nan
df = df.ffill()

# check for extreme values (>25% change in a day)
# TODO: Implement this


# Convert NIFTYBEES to USD
usdinr = yf.download("USDINR=X", period="10y")["Close"]
usdinr = usdinr.tz_localize("UTC")
df["NIFTYBEES.USD"] = df["NIFTYBEES.NS"].div(usdinr, axis=0)
df.ffill(inplace=True)

# %%
df1 = df / df.iloc[0]
df1.plot()

# Export returns data to JSON
returns_data = {
    "dates": df1.index.strftime("%Y-%m-%d").tolist(),
    "XLK": [None if pd.isna(x) else x for x in df1["XLK"].tolist()],
    "SPY": [None if pd.isna(x) else x for x in df1["SPY"].tolist()],
    "NIFTYBEES": [None if pd.isna(x) else x for x in df1["NIFTYBEES.USD"].tolist()],
}

with open("returns.json", "w") as f:
    json.dump(returns_data, f)

# %%
dd = df / df.cummax() - 1
dd[dd.isna().any(axis=1)]


# %%

# Plot the drawdowns as line plots
fig, ax = plt.subplots(figsize=(12, 6))
plt.tight_layout()  # Add this for better layout
(line1,) = ax.plot(dd.index, dd["XLK"], label="XLK", alpha=0.8)
(line2,) = ax.plot(dd.index, dd["SPY"], label="SPY", alpha=0.8)
(line3,) = ax.plot(dd.index, dd["NIFTYBEES.USD"], label="NIFTYBEES.USD", alpha=0.8)
ax.legend()
ax.set_title("Drawdowns Over 10 Years")
ax.grid(True, alpha=0.3)

# Create button axes with better positioning
plt.subplots_adjust(bottom=0.2)  # Make room for buttons
button_ax1 = plt.axes([0.2, 0.05, 0.15, 0.075])
button_ax2 = plt.axes([0.4, 0.05, 0.15, 0.075])
button_ax3 = plt.axes([0.6, 0.05, 0.15, 0.075])

# Create buttons
button_xlk = Button(button_ax1, "Toggle XLK")
button_spy = Button(button_ax2, "Toggle SPY")
button_nifty = Button(button_ax3, "Toggle NIFTY")


# Define button click handlers
def toggle_xlk(event):
    line1.set_visible(not line1.get_visible())
    fig.canvas.draw_idle()


def toggle_spy(event):
    line2.set_visible(not line2.get_visible())
    fig.canvas.draw_idle()


def toggle_nifty(event):
    line3.set_visible(not line3.get_visible())
    fig.canvas.draw_idle()


# Connect buttons to handlers
button_xlk.on_clicked(toggle_xlk)
button_spy.on_clicked(toggle_spy)
button_nifty.on_clicked(toggle_nifty)

# Export data to JSON
output_data = {
    "dates": dd.index.strftime("%Y-%m-%d").tolist(),
    "XLK": [None if pd.isna(x) else x for x in dd["XLK"].tolist()],
    "SPY": [None if pd.isna(x) else x for x in dd["SPY"].tolist()],
    "NIFTYBEES": [None if pd.isna(x) else x for x in dd["NIFTYBEES.USD"].tolist()],
}


with open("data.json", "w") as f:
    json.dump(output_data, f)

# Export returns data to JSON
returns_data = {
    "dates": df1.index.strftime("%Y-%m-%d").tolist(),
    "XLK": [None if pd.isna(x) else x for x in df1["XLK"].tolist()],
    "SPY": [None if pd.isna(x) else x for x in df1["SPY"].tolist()],
    "NIFTYBEES": [None if pd.isna(x) else x for x in df1["NIFTYBEES.USD"].tolist()],
}

with open("returns.json", "w") as f:
    json.dump(returns_data, f)

plt.show()
