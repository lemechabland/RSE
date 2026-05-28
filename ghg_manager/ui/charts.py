"""Chart utilities for visualization in the GHG Manager."""

from matplotlib.figure import Figure


def build_scope_chart(totals: dict) -> Figure:
    figure = Figure(figsize=(6, 4))
    axes = figure.subplots()
    labels = [key for key in totals.keys() if key.startswith("scope_")]
    values = [totals.get(key, 0.0) for key in labels]
    axes.bar(labels, values, color=["#4c72b0", "#55a868", "#c44e52"])
    axes.set_title("GHG Emissions by Scope")
    axes.set_ylabel("CO2e")
    axes.grid(axis="y", linestyle="--", alpha=0.5)
    return figure
