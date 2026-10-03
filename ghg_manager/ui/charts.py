"""Chart utilities for visualization in the GHG Manager."""

from matplotlib.figure import Figure

SCOPE_COLORS = ["#0f766e", "#475569", "#d97706"]


def build_scope_chart(totals: dict) -> Figure:
    figure = Figure(figsize=(6, 4))
    figure.set_facecolor("#ffffff")
    axes = figure.subplots()
    axes.set_facecolor("#ffffff")
    labels = [key for key in totals.keys() if key.startswith("scope_")]
    values = [totals.get(key, 0.0) for key in labels]
    axes.bar(labels, values, color=SCOPE_COLORS[: len(labels)])
    axes.set_title("GHG Emissions by Scope", color="#1e293b", fontweight="bold")
    axes.set_ylabel("CO2e")
    axes.tick_params(colors="#64748b")
    axes.spines["top"].set_visible(False)
    axes.spines["right"].set_visible(False)
    axes.spines["left"].set_color("#dde3ea")
    axes.spines["bottom"].set_color("#dde3ea")
    axes.grid(axis="y", linestyle="--", color="#dde3ea", alpha=0.7)
    axes.set_axisbelow(True)
    return figure
