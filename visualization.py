import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Patch


def plot_sector_npps_heatmap(beats, title="Sector-Level WLS Heatmap in Berkeley Police Patrol"):
    """
    Plot sector boundaries with NPPS heatmap.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    cmap = plt.cm.Reds
    norm = mcolors.Normalize(vmin=beats["sector_total_npps"].min(),
                            vmax=beats["sector_total_npps"].max())
    beats.plot(column="sector_total_npps", cmap=cmap, norm=norm,
               edgecolor="black", linewidth=1, alpha=0.7, ax=ax)
    beats["centroid"] = beats.geometry.centroid
    for idx, row in beats.iterrows():
        ax.text(row["centroid"].x, row["centroid"].y,
                f"{int(row['Sector'])}",
                fontsize=10, color="black", ha="center", va="center", fontweight="bold")
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
    cbar.set_label("Total WLS per Sector", fontsize=12)
    ax.set_title(title, fontsize=14)
    ax.set_axis_off()
    plt.show()


def plot_moved_grids(grid, moved_ids, beats, title="Grid Transfers from Excess Sectors"):
    """
    Plot grid transfers (moved grids) with sector boundaries.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    grid.plot(ax=ax, facecolor="lightgray", edgecolor="black", linewidth=0.2)
    grid[grid["Grid_ID"].isin(moved_ids)].plot(
        ax=ax, facecolor="yellow", edgecolor="red", linewidth=1, label="Moved Grids"
    )
    beats.boundary.plot(ax=ax, color="black", linestyle="--", linewidth=1.5)
    ax.set_title(title)
    ax.legend()
    ax.set_axis_off()
    plt.show()


def visualize_comparison(original_grid, snapped_sectors, streets):
    """
    Create a visualization comparing original and snapped sectors with streets.
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
    original_sectors = original_grid.dissolve(by="Sector")
    streets.plot(ax=ax1, color='gray', linewidth=0.5, alpha=0.5)
    original_sectors.boundary.plot(ax=ax1, color='black', linewidth=1.5)
    ax1.set_title("Original Sector Boundaries")
    ax1.set_axis_off()
    streets.plot(ax=ax2, color='gray', linewidth=0.5, alpha=0.5)
    snapped_sectors.boundary.plot(ax=ax2, color='black', linewidth=1.5)
    ax2.set_title("Snapped Sector Boundaries")
    ax2.set_axis_off()
    plt.tight_layout()
    plt.show()


def plot_final_sectors(snapped_sectors):
    """
    Plot final snapped sectors with sector labels.
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    snapped_sectors.boundary.plot(
        ax=ax,
        color='black',
        linewidth=1.5,
        alpha=1.0
    )
    snapped_sectors["centroid"] = snapped_sectors.geometry.centroid
    for idx, row in snapped_sectors.iterrows():
        ax.text(row["centroid"].x, row["centroid"].y,
                f"{int(row['Sector'])}",
                fontsize=10, color="black", ha="center", va="center", fontweight="bold")
    ax.set_title("Berkeley Police Department Sectors", fontsize=14)
    ax.set_axis_off()
    plt.tight_layout()
    plt.show() 