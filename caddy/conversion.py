import logging
from copy import copy, deepcopy
from dataclasses import dataclass
from typing import Iterable, Optional, Tuple, Union

import shapely
from ezdxf.addons import geo
from ezdxf.entities import (
    DXFEntity,
    DXFGraphic,
    Dimension,
    Insert,
    MText,
    Text,
    Circle,
    Arc,
)
from ezdxf.layouts import BlockLayout
from ezdxf.math import Matrix44, basic_transformation

TRANSFORM = False
logger = logging.getLogger(__name__)

__all__ = ["to_shapely", "BlockInsertion"]


@dataclass
class BlockInsertion:
    block: BlockLayout
    insertion: Insert


def to_shapely(
    entity: DXFEntity,
    m: Matrix44 = None,
    step_size: float = 0.1,
    precision: float = 10,
) -> Optional[Tuple[shapely.geometry.base.BaseGeometry, Union[DXFEntity, BlockLayout]]]:
    if isinstance(entity, Insert):
        if False:
            multiplier = 10
            vec3 = entity.dxf.insert

            x, y, z = vec3.x, vec3.y, vec3.z
            rotation = entity.dxf.rotation
            xs, ys, zs = entity.dxf.xscale, entity.dxf.xscale, entity.dxf.xscale

            left_ = vec3 * basic_transformation(
                (x - multiplier, y - multiplier, z - multiplier), z_rotation=rotation
            )

            to_ = vec3 * basic_transformation(
                (xs * multiplier, ys * multiplier, zs * multiplier), z_rotation=rotation
            )

            yield shapely.LineString(
                [(left_.x, left_.y), (x, y), (to_.x, to_.y)]
                # , vec3.z
            ), entity.block()
            # TODO: Box of scale WITH THE BEARING from rotation
        else:
            vec3 = entity.dxf.insert

            x, y, z = vec3.x, vec3.y, vec3.z
            yield shapely.Point(x, y), BlockInsertion(
                entity.block(), entity
            )  # deepcopy(entity))

        entity_query = (
            entity.virtual_entities()
        )  # entity.explode() # WARNING, PERMUTEs THE insert entity
        for ent in entity_query:
            yield from to_shapely(ent, m)

    elif isinstance(entity, (MText, Text)):
        vec3 = entity.dxf.insert
        yield shapely.Point(
            vec3.x,
            vec3.y,
            # , vec3.z
        ), entity

    elif isinstance(entity, Dimension):
        ...
        # logger.info(f"Skipping dimension conversion {entity}")

    elif isinstance(entity, Arc):  # TODO: ALSO CIRCLE?
        ...  # TODO: NOT SUPPORT ATM
        # logger.info(f"Skipping circle conversion {entity}")

    elif isinstance(entity, (DXFGraphic, Iterable)):
        try:
            geo_proxy = geo.proxy(entity, distance=step_size, force_line_string=False)

            geo_proxy.places = precision

            if TRANSFORM:
                # Transform DXF WCS coordinates into CRS coordinates:
                geo_proxy.wcs_to_crs(m)
                # Transform 2D map projection EPSG:3395 into globe (polar)
                # representation EPSG:4326
                geo_proxy.map_to_globe()

            geom = shapely.geometry.shape(geo_proxy)
            yield geom, entity

        except Exception as e:
            logger.warning(entity)
            ...
    else:
        ##logger.warning(entity)
        ...

    # logger.warning("Done")

    return
