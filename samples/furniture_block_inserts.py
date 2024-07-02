import random
from collections import defaultdict
from pathlib import Path
from typing import List

import shapely
from geopandas import GeoDataFrame
from jord.shapely_utilities import dilate
from matplotlib import pyplot
from numpy import cos, radians, sin
from shapely import plotting
from shapely.affinity import affine_transform
from warg import QuadNumber

from caddy.exporting import BlockPointInsert, get_block_geoms


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


if __name__ == "__main__":

    PLOT = False

    my = iter(random_rgba())

    masks = defaultdict(list)

    for f in Path(r"S:\Geodata\Indoor\FordMotors\5215_PDC\geodata\cad\00").rglob(
        "*fur.dxf"
    ):

        for block_name, block in get_block_geoms(f).items():

            geoms = shapely.GeometryCollection(block["geometries"])
            block_color = next(my)

            for insertion_point in block["inserts"]:
                transformed_geoms = affine_transform(
                    geoms, get_transformation(insertion_point)
                )

                buffered = shapely.unary_union(dilate(transformed_geoms, distance=5))

                if PLOT:
                    plotting.plot_polygon(buffered, add_points=False, color=block_color)

                masks[block_name].append(buffered)

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

    if PLOT:
        pyplot.show()
