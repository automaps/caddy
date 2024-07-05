import random
from collections import defaultdict
from pathlib import Path
from typing import List

import shapely
from caddy.exporting import BlockPointInsert, get_block_geoms
from draugr.progress_bars import progress_bar
from geopandas import GeoDataFrame
from jord.shapely_utilities import dilate
from matplotlib import pyplot
from numpy import cos, radians, sin
from shapely import plotting
from shapely.affinity import affine_transform
from warg import QuadNumber


def get_transformation(insertion_point: BlockPointInsert) -> List[float]:
    if insertion_point.matrix44:
        m = insertion_point.matrix44.get_2d_transformation()  # row wise
        return [m[0], m[3], m[1], m[4], m[6], m[7]]

    angle = radians(insertion_point.rotation)
    cos_angle = cos(angle)
    sin_angle = sin(angle)

    return [
        insertion_point.x_scale * cos_angle,
        insertion_point.y_scale * -sin_angle,
        insertion_point.x_scale * sin_angle,
        insertion_point.y_scale * cos_angle,
        insertion_point.point.x,
        insertion_point.point.y,
    ]


def random_rgba(mix: QuadNumber = (1, 1, 1, 1)) -> QuadNumber:
    while 1:
        red = random.random() * mix[0]
        green = random.random() * mix[1]
        blue = random.random() * mix[2]
        alpha = 1.0  # random.random() * mix[3]
        yield (red, green, blue, alpha)


def plot_geom(geom, color) -> None:
    if isinstance(geom, shapely.GeometryCollection):
        for g in geom.geoms:
            plot_geom(g, color)
    elif isinstance(geom, (shapely.LineString, shapely.MultiLineString)):
        plotting.plot_line(geom, add_points=False, color=color)
    elif isinstance(geom, (shapely.Point, shapely.MultiPoint)):
        plotting.plot_points(geom, add_points=False, color=color)
    else:
        plotting.plot_polygon(geom, add_points=False, color=color)


if __name__ == "__main__":

    def auh(plot: bool = False) -> None:

        color_generator = iter(random_rgba())

        masks = defaultdict(list)

        files = list(
            Path(r"S:\Geodata\Indoor\FordMotors\5091\geodata\cad\dxf").rglob("*fur.dxf")
        )

        for f in progress_bar(files):
            for block_name, block in progress_bar(get_block_geoms(f).items()):

                geoms = shapely.GeometryCollection(block["geometries"])

                buffered = shapely.unary_union(
                    dilate(shapely.unary_union(geoms), distance=1)
                )

                for insertion_point in progress_bar(block["inserts"]):
                    transformed_geoms = affine_transform(
                        buffered, get_transformation(insertion_point)
                    )

                    if plot:
                        plot_geom(transformed_geoms, color=next(color_generator))

                    masks[block_name].append(transformed_geoms)

            gdf = GeoDataFrame(
                (
                    {"name": block_name, "geometry": instance}
                    for block_name, instances in masks.items()
                    for instance in instances
                ),
                geometry="geometry",
                crs=3857,
            )

            with open(f"{f.stem}-blocks.geojson", "w") as f:
                f.write(gdf.to_json())

            if plot:
                pyplot.show()

    auh()
