import geopandas as gpd
from shapely.geometry import box
import config


def create_grid(beats):
    """
    Create a grid of square cells covering the bounds of the beats GeoDataFrame.
    Returns a GeoDataFrame of grid cells.
    """
    minx, miny, maxx, maxy = beats.total_bounds
    cell_size = config.CELL_SIZE
    grid_cells = []
    x = minx
    while x < maxx:
        y = miny
        while y < maxy:
            cell = box(x, y, x + cell_size, y + cell_size)
            grid_cells.append(cell)
            y += cell_size
        x += cell_size
    grid = gpd.GeoDataFrame(geometry=grid_cells, crs=beats.crs)
    return grid


def assign_sectors_to_grid(grid, beats):
    """
    Assign each grid cell to a sector based on centroid spatial join.
    Returns the grid with 'Sector' and 'Grid_ID' columns.
    """
    # Calculate centroids
    grid["centroid"] = grid.geometry.centroid
    centroids = grid.copy()
    centroids["geometry"] = centroids["centroid"]
    # Spatial join
    centroids_sjoined = gpd.sjoin(
        centroids,
        beats,
        how="left",
        predicate="intersects"
    ).reset_index(drop=True)
    grid["Sector"] = centroids_sjoined["Sector"]
    # Drop cells with no sector assignment
    grid = grid.dropna(subset=["Sector"])
    grid["Sector"] = grid["Sector"].astype(int)
    grid["Grid_ID"] = grid.index
    return grid


def identify_boundary_grids(grid):
    """
    Identify boundary grids (grids that touch a neighbor with a different sector).
    Returns a GeoDataFrame with an 'is_boundary' column (True/False).
    """
    boundary_grids = grid.copy()
    boundary_grids["is_boundary"] = False
    for idx, row in grid.iterrows():
        neighbors = grid[grid.geometry.touches(row.geometry)]
        if not neighbors.empty:
            if any(neighbors["Sector"] != row["Sector"]):
                boundary_grids.at[idx, "is_boundary"] = True
    return boundary_grids 