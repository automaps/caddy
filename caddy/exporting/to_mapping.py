import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

import ezdxf
from ezdxf.entities import DXFEntity, Insert, MText, Text
from ezdxf.math import Matrix44
from jord.shapely_utilities import clean_shape

from caddy.conversion import to_shapely
from caddy.model import BlockInsertion, FailCase

logger = logging.getLogger(__name__)

__all__ = ["export_to_shapely_dict"]


def export_to_shapely_dict(dxf_path: Path) -> List[Dict]:
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

    geoms = defaultdict(list)
    for entity in msp.query("*"):
        for g, e in to_shapely(entity, m):
            if g:
                if isinstance(e, DXFEntity):
                    cleaned = clean_shape(g)
                    geoms[e.dxf.layer].append((cleaned, e))
                elif isinstance(e, BlockInsertion):
                    # logger.warning(f"Found block layout {e}")
                    geoms[f"BLOCK_INSERTS_OF_{e.block.name}"].append((g, e.insertion))
                elif isinstance(e, FailCase):
                    # logger.warning(f"Found fail case {e}")
                    geoms[f"FAIL_CASE_{e.entity.dxf.layer}"].append((g, e.entity))

                else:
                    logger.error(f"Unexpected entity type {type(e)}")
            else:
                logger.error(f"{entity} has no geometry ")

    extras = defaultdict(list)
    for l, ges in dict(geoms).items():
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

    return extras
