# config.py

# File paths
SHAPEFILE_PATH = "bpd_final/Balanced_Beats_V2.shp"
YEAR_DATA_PATH = "bpd_final/2024.csv"
CENTERLINES_PATH = "bpd_final/Centerlines.shp"
FINAL_GRID_PATH = "bpd_final/final_grid.shp"
SNAPPED_SECTORS_PATH = "bpd_final/output/snapped_sectors.shp"

# Grid parameters
CELL_SIZE = 0.001  # 100m grid

# NPPS weights
PRIORITY_WEIGHTS = {1: 1.0, 2: 0.7, 3: 0.4, 4: 0.2, 5: 0.1}
NPPS_WEIGHTS = {
    "priority": 0.7,
    "response_time": 0.1,
    "disposition": 0.2
}

# Outlier handling
OUTLIER_METHOD = "IQR"
OUTLIER_REPLACEMENT = 0

# Snapping parameters
SNAP_TOLERANCE = 50  # meters

# Sector neighbors
def get_sector_neighbors():
    return {
        1: [2],
        2: [1, 3, 4, 14],
        3: [2, 4, 5, 11, 12, 14],
        4: [2, 3, 5, 6],
        5: [3, 4, 6, 9, 10, 11],
        6: [4, 5, 7, 8, 9],
        7: [6, 8],
        8: [6, 7, 9],
        9: [5, 6, 8, 10],
        10: [5, 9, 11],
        11: [3, 5, 10, 12],
        12: [3, 11, 13],
        13: [12, 14],
        14: [2, 3, 13]
    } 