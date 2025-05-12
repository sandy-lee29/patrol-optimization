import geopandas as gpd
import pandas as pd

def build_boundary_pairs_info(grid: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Find all grid cells that are on the boundary between different sectors.
    Returns a GeoDataFrame with columns: Grid_ID, Sector, neighbor_sector, geometry
    """
    boundary_list = []
    for idx, row in grid.iterrows():
        from_sector = row["Sector"]
        neighbors = grid[grid.geometry.touches(row.geometry)]
        diff_sector_neighbors = neighbors[neighbors["Sector"] != from_sector]
        for n_idx, n_row in diff_sector_neighbors.iterrows():
            boundary_list.append({
                "Grid_ID": row["Grid_ID"],
                "Sector": from_sector,
                "neighbor_sector": n_row["Sector"],
                "geometry": row["geometry"]
            })
    boundary_pairs_info = gpd.GeoDataFrame(boundary_list, crs=grid.crs)
    boundary_pairs_info.drop_duplicates(subset=["Grid_ID", "Sector", "neighbor_sector"], inplace=True)
    return boundary_pairs_info


def recalc_sector_npps_sum(grid: gpd.GeoDataFrame) -> pd.DataFrame:
    """
    Recalculate sector NPPS sum from the grid.
    Returns DataFrame: Sector, sector_total_npps
    """
    new_sum = grid.groupby("Sector")["total_npps"].sum().reset_index()
    new_sum.rename(columns={"total_npps": "sector_total_npps"}, inplace=True)
    return new_sum


def print_npps_diff(old_sum: pd.DataFrame, new_sum: pd.DataFrame, sector_list: list):
    """
    Print NPPS difference for specified sectors.
    """
    merged = old_sum.merge(new_sum, on="Sector", suffixes=("_old", "_new"))
    merged["npps_diff"] = merged["sector_total_npps_new"] - merged["sector_total_npps_old"]
    filtered = merged[merged["Sector"].isin(sector_list)]
    print(filtered[["Sector", "sector_total_npps_old", "sector_total_npps_new", "npps_diff"]])


def take_boundary_from_neighbor(grid: gpd.GeoDataFrame, boundary_pairs_info: gpd.GeoDataFrame,
                               from_sector: int, to_sector: int):
    """
    Move all boundary grids from from_sector to to_sector.
    Returns updated grid and list of moved Grid_IDs.
    """
    target_boundary = boundary_pairs_info[
        (boundary_pairs_info["Sector"] == from_sector) &
        (boundary_pairs_info["neighbor_sector"] == to_sector)
    ]
    moved_ids = target_boundary["Grid_ID"].unique()
    if len(moved_ids) == 0:
        return grid, []
    grid.loc[grid["Grid_ID"].isin(moved_ids), "Sector"] = to_sector
    return grid, moved_ids.tolist()


def give_bulk_boundaries_from_excess(grid: gpd.GeoDataFrame, sector_neighbors: dict, excess_sectors: list):
    """
    Excess sectors give all their boundary grids to non-excess neighbors.
    Returns updated grid and list of all moved grid IDs.
    """
    boundary_pairs_info = build_boundary_pairs_info(grid)
    moved_all = []
    old_sum = recalc_sector_npps_sum(grid)
    eligible_donors = sorted(
        [s for s in excess_sectors],
        key=lambda s: len([n for n in sector_neighbors[s] if n not in excess_sectors])
    )
    for donor in eligible_donors:
        recipients = [n for n in sector_neighbors[donor] if n not in excess_sectors]
        print(f"\n🔁 Sector {donor} attempts to give boundary grids to: {recipients}")
        for recipient in recipients:
            old_local_sum = recalc_sector_npps_sum(grid)
            grid, moved_ids = take_boundary_from_neighbor(grid, boundary_pairs_info, donor, recipient)
            if len(moved_ids) > 0:
                moved_all.extend(moved_ids)
                new_local_sum = recalc_sector_npps_sum(grid)
                print(f"✅ Moved {len(moved_ids)} grids from Sector {donor} ➝ {recipient}")
                print_npps_diff(old_local_sum, new_local_sum, [donor, recipient])
    final_sum = recalc_sector_npps_sum(grid)
    print("\n📊 Final NPPS (partial):")
    print(final_sum.sort_values("Sector"))
    return grid, moved_all


def take_bulk_boundaries_to_deficient(grid: gpd.GeoDataFrame, deficient_sector: int, neighbors: list):
    """
    Deficient sector pulls boundary grids from its neighbors.
    Returns updated grid and list of all moved grid IDs.
    """
    boundary_pairs_info = build_boundary_pairs_info(grid)
    moved_all = []
    old_sum = recalc_sector_npps_sum(grid)
    print(f"\n🟢 Sector {deficient_sector} attempts to pull grids from neighbors: {neighbors}")
    for nbr in neighbors:
        old_local_sum = recalc_sector_npps_sum(grid)
        grid, moved_ids = take_boundary_from_neighbor(grid, boundary_pairs_info, nbr, deficient_sector)
        if len(moved_ids) > 0:
            moved_all.extend(moved_ids)
            new_local_sum = recalc_sector_npps_sum(grid)
            print(f"✅ Moved {len(moved_ids)} grids from Sector {nbr} ➝ {deficient_sector}")
            print_npps_diff(old_local_sum, new_local_sum, [nbr, deficient_sector])
        else:
            print(f"⚠️ No boundary grids moved from Sector {nbr} ➝ {deficient_sector} (already transferred or not adjacent)")
    final_sum = recalc_sector_npps_sum(grid)
    print("\n📊 Final NPPS (partial):")
    print(final_sum.sort_values("Sector"))
    return grid, moved_all 