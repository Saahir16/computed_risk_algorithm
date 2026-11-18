"""
This file is for keeping the styling consistent across all the figures and is imported by the other figure scripts. 
The contextual framework is in teal. The rule based methods are shown in coral.
"""

import os
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

dark_text = "#0b0b0b"
gray_text = "#52514e"
grid_color = "#e1e0d9"
axis_color = "#c3c2b7"
teal = "#2f6f6a"
coral = "#d9826b"
light_coral = "#efc4b8"

teal_scale = LinearSegmentedColormap.from_list("teal_scale", ["#d9ebe8", "#9ccdc6", "#5aa39a", "#2f6f6a", "#17403c"])

def setup():
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "savefig.facecolor": "white",
            "font.size": 11,
            "text.color": dark_text,
            "axes.labelcolor": gray_text,
            "xtick.color": gray_text,
            "ytick.color": gray_text,
            "axes.edgecolor": axis_color,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
        }
    )

def clean(ax, grid_axis="y"):
    if grid_axis:
        ax.grid(axis=grid_axis, color=grid_color, linewidth=0.8)
        ax.set_axisbelow(True)
    ax.tick_params(length=0)

def save(fig, name):
    os.makedirs("figures", exist_ok=True)
    path = f"figures/{name}.png"
    fig.savefig(path, dpi=300, bbox_inches="tight")
    print("saved", path)