import geopandas as gpd
import pandas as pd
import config
import data_preprocessing as dp
import grid_utils as gu
import npps_analysis as na
import sector_optimization as so
import snapping as sn
import visualization as vis


def main():
    # Load data
    beats = dp.load_shapefile()
    df = dp.load_incident_data()
    new_df = dp.preprocess_incident_data(df)
    npps_data = dp.calculate_npps(new_df)

    # Create and assign grid
    grid = gu.create_grid(beats)
    grid = gu.assign_sectors_to_grid(grid, beats)
    boundary_grids = gu.identify_boundary_grids(grid)

    # Aggregate NPPS by grid and sector
    grid = na.aggregate_npps_by_grid(npps_data, grid)
    sector_npps_sum = na.aggregate_npps_by_sector(grid)
    beats = beats.merge(sector_npps_sum, on="Sector", how="left")

    # Visualize initial NPPS heatmap
    vis.plot_sector_npps_heatmap(beats, title="Initial Sector-Level WLS Heatmap")

    # Optimize sectors
    excess_sectors = [4, 6, 7]  # Example excess sectors
    grid, moved_ids = so.give_bulk_boundaries_from_excess(grid, config.get_sector_neighbors(), excess_sectors)
    vis.plot_moved_grids(grid, moved_ids, beats, title="Grid Transfers from Excess Sectors")

    deficient_sector = 12
    neighbors_12 = [3, 11, 13]
    grid, moved_ids = so.take_bulk_boundaries_to_deficient(grid, deficient_sector, neighbors_12)
    vis.plot_moved_grids(grid, moved_ids, beats, title="Grid Transfers to Deficient Sector")

    # Evaluate NPPS balance
    old_sum = sector_npps_sum
    new_sum = na.aggregate_npps_by_sector(grid)
    evaluation_result = na.evaluate_npps_balance(old_sum, new_sum)

    # Snap boundaries to streets
    streets = gpd.read_file(config.CENTERLINES_PATH)
    snapped_sectors = sn.smooth_sectors(grid, streets)
    vis.visualize_comparison(grid, snapped_sectors, streets)
    vis.plot_final_sectors(snapped_sectors)

    # Save final grid
    grid.to_file(config.FINAL_GRID_PATH)
    print("Final optimized grid saved as final_grid.shp")


if __name__ == "__main__":
    main() 