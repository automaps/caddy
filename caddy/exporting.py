import logging
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import ezdxf
import shapely.geometry.base
from ezdxf.math import Matrix44
from geopandas import GeoDataFrame

__all__ = ["export_to", "BlockPointInsert", "get_block_geoms"]

from jord.shapely_utilities.base import clean_shape
from jord.shapely_utilities.polygons import ensure_cw_poly, is_polygonal
from ezdxf.entities import DXFEntity, MText, Text, Insert
from .conversion import to_shapely, BlockInsertion, FailCase
from typing import Optional, Dict, Tuple, Collection, List

logger = logging.getLogger(__name__)

LAYER_WISE = False

def export_to(
    dxf_path: Path, out_path: Optional[Path] = None, driver: str = "GPKG"
    ) -> None:
  if out_path is None:
    out_path = Path(dxf_path).with_suffix(".gpkg")

  dxf_entities = extract_shaped_dxf_entities(dxf_path)

  if False:
    for block in source_doc.blocks:
      for entity in block.entity_space:
        for g, e in to_shapely(entity, m):
          if g:
            if isinstance(e, DXFEntity):
              cleaned = clean_shape(g)
              if False:
                if is_polygonal(cleaned):
                  cleaned = ensure_cw_poly(cleaned)
              dxf_entities[f"BLOCK_{block.name}"].append((cleaned, e))
            elif isinstance(e, BlockInsertion):
              # logger.warning(f"Found block layout {e}")
              dxf_entities[f"BLOCK_{block.name}"].append((g, e.insertion))

            else:
              logger.error(f"Unexpected entity type {type(e)}")
          else:
            logger.error(f"{entity} has no geometry ")

  logger.warning(f"Exporting {dxf_path} -> {out_path}")

  if LAYER_WISE:
    for l, ges in dict(dxf_entities).items():
      extras = defaultdict(list)

      g, e = zip(*ges)

      for e in e:
        if isinstance(e, (MText, Text)):
          if hasattr(e, "plain_text"):
            extras["text"].append(e.plain_text())
          else:
            extras["text"].append(e.dxf.text)
        elif isinstance(e, Insert):
          rotation = e.dxf.rotation
          xs, ys, zs = e.dxf.xscale, e.dxf.xscale, e.dxf.xscale

          extras["text"].append(f"{rotation=} {xs=} {ys=} {zs=}")
        else:
          extras["text"].append("")

      gdf = GeoDataFrame({"geometry": g, **extras})
      # gdf.crs = 'EPSG:4326'
      # gdf.to_file(str(out_path), driver=driver, layer=l)
      gdf.to_file(
          str(out_path.with_suffix(".sqlite")),
          driver="SQLite",
          spatialite=True,
          layer=l,
          )
  else:
    extras = defaultdict(list)
    for l, ges in dict(dxf_entities).items():
      g, e = zip(*ges)

      for e in e:
        if isinstance(e, (MText, Text)):
          if hasattr(e, "plain_text"):
            extras["text"].append(e.plain_text())
          else:
            extras["text"].append(e.dxf.text)
        elif isinstance(e, Insert):
          rotation = e.dxf.rotation
          xs, ys, zs = e.dxf.xscale, e.dxf.xscale, e.dxf.xscale

          extras["text"].append(f"{rotation=} {xs=} {ys=} {zs=}")
        else:
          extras["text"].append("")

      for g_ in g:
        extras["geometry"].append(g_)
        extras["layer"].append(l)

    gdf = GeoDataFrame(extras, geometry="geometry")

    # gdf.crs = 'EPSG:4326'
    if True:
      gdf.to_file(str(out_path), driver=driver)
    else:
      gdf.to_file(
          str(out_path.with_suffix(".sqlite")),
          driver="SQLite",
          spatialite=True,
          )

  logger.warning(f"Wrote {out_path}")

def extract_shaped_dxf_entities(dxf_path):
  source_doc = ezdxf.readfile(str(dxf_path))

  msp = source_doc.modelspace()
  # Store geo located DXF entities as GeoJSON data:
  # Get the geo location information from the DXF file:
  geo_data = msp.get_geodata()

  if geo_data:
    # Get transformation matrix and epsg code:
    m, epsg = geo_data.get_crs_transformation()
  else:
    # Identity matrix for DXF files without geo reference data:
    m = Matrix44()

  logger.warning(f"Converting {dxf_path}")
  shaped_dxf_entities = defaultdict(list)

  for entity in msp.query("*"):
    for shapely_geometry, dxf_entity in to_shapely(entity, m):
      if shapely_geometry:
        if isinstance(dxf_entity, DXFEntity):
          cleaned = clean_shape(shapely_geometry)
          if False:
            if is_polygonal(cleaned):
              cleaned = ensure_cw_poly(cleaned)
          shaped_dxf_entities[dxf_entity.dxf.layer].append((cleaned, dxf_entity))
        elif isinstance(dxf_entity, BlockInsertion):
          # logger.warning(f"Found block layout {e}")
          shaped_dxf_entities[f"BLOCK_INSERTS_OF_{dxf_entity.block.name}"].append(
              (shapely_geometry, dxf_entity.insertion)
              )
        elif isinstance(dxf_entity, FailCase):
          # logger.warning(f"Found fail case {e}")
          shaped_dxf_entities[f"FAIL_CASE_{dxf_entity.entity.dxf.layer}"].append(
              (shapely_geometry, dxf_entity.entity)
              )

        else:
          logger.error(f"Unexpected entity type {type(dxf_entity)}")
      else:
        logger.error(f"{entity} has no geometry ")

  return shaped_dxf_entities

@dataclass
class BlockPointInsert:
  point: shapely.Point
  rotation: float
  x_scale: float
  y_scale: float
  z_scale: float
  matrix44: Matrix44

def get_block_geoms(
    dxf_path: Path,
    ) -> Dict[
  str,
  Tuple[
    Collection[shapely.geometry.base.BaseGeometry],
    List[Tuple[shapely.Point, float, float, float, float]],
  ],
]:
  source_doc = ezdxf.readfile(str(dxf_path))

  block_geoms = defaultdict(list)

  for block in source_doc.blocks:
    for entity in block.entity_space:
      for g, e in to_shapely(entity):
        if g:
          if isinstance(e, DXFEntity):
            block_geoms[block.name].append(clean_shape(g))
          elif isinstance(e, BlockInsertion):
            logger.info(f"Nested insert of {e.block}")
        else:
          logger.error(f"{entity} has no geometry ")

  msp = source_doc.modelspace()

  block_inserts = defaultdict(list)

  for entity in msp.query("*"):
    for g, e in to_shapely(entity):
      if isinstance(e, BlockInsertion):
        block_inserts[e.block.name].append((g, e.insertion))

  block_out = {}

  for name, t in block_inserts.items():
    block_out[name] = {"geometries": block_geoms[name], "inserts": []}

    for g, e in t:
      block_out[name]["inserts"].append(
          BlockPointInsert(
              g,
              e.dxf.rotation,
              e.dxf.xscale,
              e.dxf.yscale,
              e.dxf.zscale,
              matrix44=e.matrix44(),
              )
          )

  return block_out
