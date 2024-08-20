from pathlib import Path
from typing import Optional

import geopandas
from matplotlib import pyplot

from caddy.exporting import extract_shaped_dxf_entities

def dxf_to_svg(dxf_path, out_path: Optional[Path] = None) -> None:
  if out_path is None:
    out_path = Path(dxf_path).with_suffix(".svg")

  layers = []

  for layer, shaped_entities in extract_shaped_dxf_entities(dxf_path).items():
    shapes, meta = zip(*shaped_entities)
    for shape in shapes:
      layers.append({'geometry': shape, 'layer': layer})

  # frame = geopandas.GeoDataFrame.from_dict(layers, orient="index")
  frame = geopandas.GeoDataFrame(layers, geometry='geometry')
  frame.plot()

  pyplot.savefig(out_path)
  # pyplot.show()

def dxf_to_pyplot(dxf_path, out_path: Optional[Path] = None) -> None:
  if out_path is None:
    out_path = Path(dxf_path).with_suffix(".pdf")

  layers = []

  for layer, shaped_entities in extract_shaped_dxf_entities(dxf_path).items():
    shapes, meta = zip(*shaped_entities)
    for shape in shapes:
      layers.append({'geometry': shape, 'layer': layer})

  # frame = geopandas.GeoDataFrame.from_dict(layers, orient="index")
  frame = geopandas.GeoDataFrame(layers, geometry='geometry')
  frame.plot()

  pyplot.savefig(out_path)
  # pyplot.show()

def dxf_to_rasterio(dxf_path, out_path: Optional[Path] = None) -> None:
  if out_path is None:
    out_path = Path(dxf_path).with_suffix(".tif")

  layers = []

  for layer, shaped_entities in extract_shaped_dxf_entities(dxf_path).items():
    shapes, meta = zip(*shaped_entities)
    for shape in shapes:
      layers.append({'geometry': shape, 'layer': layer})

  # frame = geopandas.GeoDataFrame.from_dict(layers, orient="index")
  frame = geopandas.GeoDataFrame(layers, geometry='geometry')

  src = rasterio.open(inras)

  def getFeatures(gdf):
    """Function to parse features from GeoDataFrame in such a manner that rasterio wants them"""
    import json

    return [json.loads(gdf.to_json())['features'][0]['geometry']]

  coords = getFeatures(df)
  clipped_array, clipped_transform = mask(dataset=src, shapes=coords, crop=True)

  df = df.to_crs(src.crs)
  out_meta = src.meta.copy()
  out_meta.update(
      {
          "driver": "GTiff",
          "height": clipped_array.shape[1],
          "width": clipped_array.shape[2],
          "transform": clipped_transform
          }
      )
  out_tif = "clipped_example.tif"
  with rasterio.open(out_tif, "w", **out_meta) as dest:
    dest.write(clipped_array)

  clipped = rasterio.open(out_tif)
  fig, ax = plt.subplots(figsize=(8, 6))
  p1 = df.plot(color=None, facecolor='none', edgecolor='red', linewidth=2, ax=ax)
  show(clipped, ax=ax)
  ax.axis('off');

  pyplot.savefig(out_path)
  # pyplot.show()

if __name__ == '__main__':
  dxf_to_svg(
      Path(r'C:\Users\chen\Projects\MapsPeople\mi_companion\caddy\tests\fixtures\Z0_Groundfloor_Jacuna.dxf')
      )
