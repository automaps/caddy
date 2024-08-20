from collections import defaultdict
from pathlib import Path

import shapely
from draugr.progress_bars import progress_bar
from geopandas import GeoDataFrame
from jord.shapely_utilities import dilate
from matplotlib import pyplot
from shapely.affinity import affine_transform

from caddy.exporting import get_block_geoms
from caddy.helpers import get_transformation, plot_shapely_geometry, random_rgba

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
            plot_shapely_geometry(transformed_geoms, color=next(color_generator))

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
