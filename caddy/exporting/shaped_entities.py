import logging
from collections import defaultdict
from pathlib import Path
from typing import List

import ezdxf
from ezdxf.entities import DXFEntity
from ezdxf.math import Matrix44

from caddy.conversion import to_shapely
from caddy.model import BlockInsertion, FailCase
from jord.shapely_utilities import clean_shape, ensure_cw_poly, is_polygonal

logger = logging.getLogger(__name__)

__all__ = ["extract_shaped_dxf_entities"]


def extract_shaped_dxf_entities(dxf_path: Path) -> List[DXFEntity]:
    if not isinstance(dxf_path, Path):
        dxf_path = Path(dxf_path)

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
                    if True:
                        cleaned = clean_shape(shapely_geometry)
                    else:
                        cleaned = shapely_geometry
                    if False:
                        if is_polygonal(cleaned):
                            cleaned = ensure_cw_poly(cleaned)
                    shaped_dxf_entities[dxf_entity.dxf.layer].append(
                        (cleaned, dxf_entity)
                    )
                elif isinstance(dxf_entity, BlockInsertion):
                    # logger.warning(f"Found block layout {e}")
                    shaped_dxf_entities[
                        f"BLOCK_INSERTS_OF_{dxf_entity.block.name}"
                    ].append((shapely_geometry, dxf_entity.insertion))
                elif isinstance(dxf_entity, FailCase):
                    # logger.warning(f"Found fail case {e}")
                    shaped_dxf_entities[
                        f"FAIL_CASE_{dxf_entity.entity.dxf.layer}"
                    ].append((shapely_geometry, dxf_entity.entity))

                else:
                    logger.error(f"Unexpected entity type {type(dxf_entity)}")
            else:
                logger.error(f"{entity} has no geometry ")

    return shaped_dxf_entities
