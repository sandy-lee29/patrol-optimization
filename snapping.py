import geopandas as gpd
import os
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
import config


def find_nearest_point_on_lines(point, lines, max_distance=50):
    """
    Find the nearest point on any line within max_distance meters.
    Returns None if no line is within max_distance.
    """
    min_dist = float('inf')
    nearest_point = None
    for line in lines:
        if line.distance(point) <= max_distance:
            p = line.interpolate(line.project(point))
            dist = point.distance(p)
            if dist < min_dist:
                min_dist = dist
                nearest_point = p
    return nearest_point if min_dist <= max_distance else None


def snap_polygon_to_streets(polygon, street_lines, tolerance=50):
    """
    Snap a single polygon's vertices to nearest street segments.
    """
    coords = list(polygon.exterior.coords)
    new_coords = []
    for i, coord in enumerate(coords[:-1]):  # Skip last point (same as first)
        point = Point(coord)
        snapped = find_nearest_point_on_lines(point, street_lines, tolerance)
        if snapped:
            new_coords.append((snapped.x, snapped.y))
        else:
            new_coords.append(coord)
    new_coords.append(new_coords[0])  # Close the polygon
    return Polygon(new_coords)


def snap_to_streets(geom, streets, tolerance=50):
    """
    Snap polygon vertices to nearest street segments within tolerance distance.
    Handles both Polygon and MultiPolygon geometries.
    """
    street_lines = [geom for geom in streets.geometry]
    if isinstance(geom, Polygon):
        return snap_polygon_to_streets(geom, street_lines, tolerance)
    elif isinstance(geom, MultiPolygon):
        snapped_polys = []
        for poly in geom.geoms:
            snapped_poly = snap_polygon_to_streets(poly, street_lines, tolerance)
            snapped_polys.append(snapped_poly)
        return MultiPolygon(snapped_polys)
    else:
        raise ValueError(f"Unsupported geometry type: {type(geom)}")


def smooth_sectors(grid, streets, output_dir="output"):
    """
    Smooth sector boundaries by snapping to nearby streets and export as shapefile.
    Args:
        grid: GeoDataFrame containing the grid-based sectors
        streets: GeoDataFrame containing street centerlines
        output_dir: Directory to save output files
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    streets = streets.to_crs(grid.crs)
    sectors = []
    for sector in sorted(grid["Sector"].unique()):
        print(f"Processing Sector {sector}...")
        sector_grids = grid[grid["Sector"] == sector]
        sector_polygon = unary_union(sector_grids.geometry)
        snapped_polygon = snap_to_streets(sector_polygon, streets, config.SNAP_TOLERANCE)
        sectors.append({
            "Sector": sector,
            "geometry": snapped_polygon
        })
    snapped_sectors = gpd.GeoDataFrame(sectors, crs=grid.crs)
    output_file = os.path.join(output_dir, "snapped_sectors.shp")
    snapped_sectors.to_file(output_file)
    print(f"Snapped sectors saved to {output_file}")
    return snapped_sectors 