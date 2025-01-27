# An interactive plot of the payoff of a short put position, including the position delta
# %%
import grynn_pylib.finance.options as options
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import numpy as np

## Set up the data
strike = 100.0
spot_ladder = np.linspace(0.70 * strike, 1.3 * strike, 100)  # 50% to 150% of strike
payoff_short_put = options.payoff_short_put(spot_ladder, strike, premium=2.8)

# Initialize the plot lines
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()  # Create a second y-axis sharing the same x-axis

# Plot on respective axes
(line1,) = ax1.plot(spot_ladder, payoff_short_put, label="Payoff Short Put", color="blue")
(line2,) = ax2.plot(spot_ladder, np.zeros_like(spot_ladder), label="Position Delta", color="green")

# Set up the plot
ax1.set_xlabel("Spot Price")
ax1.set_ylabel("Payoff", color="blue")
ax2.set_ylabel("Delta", color="green")
ax2.set_ylim(-0.1, 1.1)  # Add 10% padding to delta limits

# Get payoff limits and add 10% padding
payoff_min = min(payoff_short_put)
payoff_max = max(payoff_short_put)
padding = (payoff_max - payoff_min) * 0.1
ax1.set_ylim(payoff_min - padding, payoff_max + padding)

ax1.set_title("Short Put Position: Payoff and Delta")
ax1.axvline(x=strike, color="gray", linestyle="--", alpha=0.5)
ax1.axhline(y=0, color="gray", linestyle="-", alpha=0.3)
ax1.grid(True, alpha=0.3)

# Create slider axes
plt.subplots_adjust(top=0.85, bottom=0.2, right=0.95)  # Make room for sliders
slider_color = "lightgoldenrodyellow"

ax_dte = plt.axes([0.15, 0.1, 0.65, 0.03], facecolor=slider_color)
ax_vol = plt.axes([0.15, 0.06, 0.65, 0.03], facecolor=slider_color)
ax_rate = plt.axes([0.15, 0.02, 0.65, 0.03], facecolor=slider_color)

# Create sliders
s_dte = Slider(ax_dte, "DTE", 1, 365, valinit=30, valstep=1)
s_vol = Slider(ax_vol, "Vol", 0.05, 1.0, valinit=0.2, valstep=0.05)
s_rate = Slider(ax_rate, "Rate", 0.01, 0.10, valinit=0.05, valstep=0.01)


def update(val):
    """Update the plot when sliders change."""
    dte = s_dte.val
    vol = s_vol.val
    r = s_rate.val
    position_delta = -options.bs_delta(spot_ladder, strike, dte / 365, r, vol, option_type="put")
    line2.set_ydata(position_delta)
    ax1.set_title(f"Short Put Position (DTE: {dte:.0f}, Vol: {vol:.1%}, Rate: {r:.1%})")
    fig.canvas.draw_idle()


# Register the update function with each slider
s_dte.on_changed(update)
s_vol.on_changed(update)
s_rate.on_changed(update)

# Initial plot
update(None)

plt.show()
