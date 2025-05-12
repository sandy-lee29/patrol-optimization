import geopandas as gpd
import pandas as pd
import numpy as np


def aggregate_npps_by_grid(npps_data, grid):
    """
    Assign each NPPS point to the nearest grid cell and aggregate NPPS by grid.
    Returns the grid with a new 'total_npps' column.
    """
    npps_data = gpd.GeoDataFrame(
        npps_data,
        geometry=gpd.points_from_xy(npps_data['lon'], npps_data['lat']),
        crs="EPSG:4326"
    )
    npps_data = gpd.sjoin_nearest(npps_data, grid, how="left", distance_col="distance_to_grid")
    grid_npps_sum = npps_data.groupby("Grid_ID")["NPPS"].sum().reset_index()
    grid_npps_sum.rename(columns={"NPPS": "total_npps"}, inplace=True)
    grid = grid.merge(grid_npps_sum, on="Grid_ID", how="left")
    grid["total_npps"] = grid["total_npps"].fillna(0)
    return grid


def aggregate_npps_by_sector(grid):
    """
    Aggregate total NPPS by sector from the grid.
    Returns a DataFrame with columns: Sector, sector_total_npps
    """
    sector_npps_sum = grid.groupby("Sector")["total_npps"].sum().reset_index()
    sector_npps_sum.rename(columns={"total_npps": "sector_total_npps"}, inplace=True)
    return sector_npps_sum


def evaluate_npps_balance(old_sum: pd.DataFrame, new_sum: pd.DataFrame):
    """
    Compare NPPS balance before and after optimization.
    Prints variance, max/min ratio, and deviation from mean.
    Returns merged DataFrame for further analysis.
    """
    merged = old_sum.merge(new_sum, on="Sector", suffixes=("_old", "_new"))
    old_var = np.var(merged["sector_total_npps_old"])
    new_var = np.var(merged["sector_total_npps_new"])
    old_ratio = merged["sector_total_npps_old"].max() / merged["sector_total_npps_old"].min()
    new_ratio = merged["sector_total_npps_new"].max() / merged["sector_total_npps_new"].min()
    old_mean = merged["sector_total_npps_old"].mean()
    new_mean = merged["sector_total_npps_new"].mean()
    merged["old_dev_from_mean(%)"] = ((merged["sector_total_npps_old"] - old_mean) / old_mean) * 100
    merged["new_dev_from_mean(%)"] = ((merged["sector_total_npps_new"] - new_mean) / new_mean) * 100
    print("\n📊 **NPPS Variance Comparison** 📊")
    print(f"Before Optimization: {old_var:.2f}")
    print(f"After Optimization:  {new_var:.2f}")
    print("\n📊 **Max/Min Ratio Comparison** 📊")
    print(f"Before Optimization: {old_ratio:.2f}")
    print(f"After Optimization:  {new_ratio:.2f}")
    print("\n📊 **Deviation from Mean (%) (First 5 Sectors)** 📊")
    print(merged[["Sector", "old_dev_from_mean(%)", "new_dev_from_mean(%)"]].head(14))
    return merged


def normalized_score(value, worst, best):
    """
    Normalize a value to a 1~10 score (the lower the value, the better).
    """
    score_0_to_1 = (worst - value) / (worst - best)
    score_0_to_1 = max(min(score_0_to_1, 1), 0)
    return round(score_0_to_1 * 9 + 1, 1) 