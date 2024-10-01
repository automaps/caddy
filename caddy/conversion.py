import logging
from typing import Iterable, Optional, Tuple, Union

import shapely
from ezdxf.addons import geo
from ezdxf.entities import (
    Circle,
    DXFEntity,
    DXFGraphic,
    Dimension,
    Insert,
    MText,
    Polyline,
    Text,
)
from ezdxf.entities.image import ImageBase
from ezdxf.math import Matrix44
from jord.shapely_utilities import clean_shape

from caddy.model import BlockInsertion, FailCase

TRANSFORM = False
TRY_FIX_CURVES = False
SMALL_NUMBER = 0.0001

logger = logging.getLogger(__name__)

__all__ = ["to_shapely"]


def to_shapely(
    entity: DXFEntity,
    m: Matrix44 = None,
    step_size: float = 0.1,
    precision: float = 10,
) -> Optional[
    Tuple[
        shapely.geometry.base.BaseGeometry, Union[DXFEntity, BlockInsertion, FailCase]
    ]
]:
    if isinstance(entity, Insert):
        vec3 = entity.dxf.insert

        x, y, z = vec3.x, vec3.y, vec3.z
        yield shapely.Point(x, y), BlockInsertion(entity.block(), entity)

        for ent in entity.virtual_entities():
            yield from to_shapely(ent, m)

    elif isinstance(entity, (MText, Text)):
        vec3 = entity.dxf.insert
        yield shapely.Point(
            vec3.x,
            vec3.y,
            # , vec3.z
        ), entity

    elif isinstance(entity, Dimension):
        for ent in entity.virtual_entities():
            yield from to_shapely(ent, m)

    elif isinstance(entity, Polyline) and not (
        entity.is_3d_polyline or entity.is_2d_polyline
    ):
        poly = shapely.Polygon((p.x, p.y) for p in entity.points())

        yield clean_shape(poly), entity

    elif isinstance(entity, ImageBase):
        yield shapely.LineString((v.x, v.y) for v in entity.boundary_path), entity

    else:
        if isinstance(entity, (DXFGraphic, Iterable)):
            try:
                geo_proxy = geo.proxy(
                    entity, distance=step_size, force_line_string=False
                )

                geo_proxy.places = precision

                if TRANSFORM:
                    # Transform DXF WCS coordinates into CRS coordinates:
                    geo_proxy.wcs_to_crs(m)
                    # Transform 2D map projection EPSG:3395 into globe (polar)
                    # representation EPSG:4326
                    geo_proxy.map_to_globe()

                geom = shapely.geometry.shape(geo_proxy)
                yield geom, entity

                return

            except Exception as e:
                if False:
                    logger.error(e)

        if False:  # FAIL CASES
            if isinstance(entity, (Circle)):
                if entity.get_layout() is not None:
                    yield from to_shapely(entity.to_spline(False))

                    return

            if hasattr(entity, "vertices"):
                case = "vertices"

                if hasattr(entity.dxf, "radius") and entity.dxf.radius > 0:
                    if not TRY_FIX_CURVES:
                        logger.warning(f"skipping {entity}")
                        return

                    sagitta = step_size
                    if entity.dxf.radius < 0.1:
                        sagitta = SMALL_NUMBER
                    try:
                        geom = shapely.LineString(
                            (p.x, p.y) for p in entity.flattening(sagitta)
                        )
                        case = "radius"
                    except Exception as e:
                        logger.error(e)
                        return

                elif hasattr(entity, "flattening"):
                    geom = shapely.LineString(
                        (p.x, p.y) for p in entity.flattening(step_size)
                    )
                    case = "flattening"
                else:
                    geom = shapely.LineString((p.x, p.y) for p in entity.vertices())

                yield clean_shape(geom), FailCase(entity, case=case)

                return

        if False:
            logger.error(f"Skipping conversion of {entity=}")

    return
