import shapely
from shapely import plotting
from warg import QuadNumber


def plot_shapely_geometry(
    geom: shapely.geometry.base.BaseGeometry, color: QuadNumber
) -> None:
    if isinstance(geom, shapely.GeometryCollection):
        for g in geom.geoms:
            plot_shapely_geometry(g, color)
    elif isinstance(geom, (shapely.LineString, shapely.MultiLineString)):
        plotting.plot_line(geom, add_points=False, color=color)
    elif isinstance(geom, (shapely.Point, shapely.MultiPoint)):
        plotting.plot_points(geom, add_points=False, color=color)
    else:
        plotting.plot_polygon(geom, add_points=False, color=color)
