import logging
from collections import defaultdict
from pathlib import Path
from typing import Collection, Dict, List, Tuple

import ezdxf
import shapely.geometry
from ezdxf.entities import DXFEntity
from jord.shapely_utilities import clean_shape

from caddy.conversion import to_shapely
from caddy.model import BlockInsertion, BlockPointInsert

logger = logging.getLogger(__name__)


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
