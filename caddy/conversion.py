import logging
from typing import Iterable, Optional, Tuple

import shapely
from ezdxf.addons import geo
from ezdxf.entities import DXFEntity, DXFGraphic, Insert, MText, Text
from ezdxf.math import Matrix44
from ezdxf.query import EntityQuery

TRANSFORM = False
logger = logging.getLogger(__name__)

__all__ = ["to_shapely"]


def to_shapely(
    entity: DXFEntity, m: Matrix44 = None, step_size: float = 0.1
) -> Optional[Tuple[shapely.geometry.base.BaseGeometry, DXFEntity]]:
    if isinstance(entity, Insert):
        entities: EntityQuery = entity.explode()
        # entities.groupby()
        for ent in entities:
            yield from to_shapely(ent, m)

        return

    elif isinstance(entity, (MText, Text)):
        vec3 = entity.dxf.insert
        yield shapely.Point(
            vec3.x,
            vec3.y,
            # , vec3.z
        ), entity

    elif isinstance(entity, (DXFGraphic, Iterable)):
        try:
            geo_proxy = geo.proxy(entity, distance=step_size, force_line_string=False)

            geo_proxy.places = 10  # Infinite precision

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
        logger.warning(entity)
        ...
