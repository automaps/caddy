import logging
from typing import Generator, Iterable, Tuple, Union

import shapely
from ezdxf.addons import geo
from ezdxf.disassemble import recursive_decompose
from ezdxf.entities import (
    Arc,
    Circle,
    DXFEntity,
    DXFGraphic,
    Dimension,
    Face3d,
    Insert,
    MText,
    Polyline,
    Text,
    Viewport,
)
from ezdxf.entities.image import ImageBase
from ezdxf.math import Matrix44
from jord.shapely_utilities import clean_shape

from caddy.model import BlockInsertion, FailCase

TRANSFORM = False
TRY_FIX_CURVES = False
SMALL_NUMBER = 0.0001
DEFAULT_STEP_SIZE = 0.1
DEFAULT_PRECISION = 10

logger = logging.getLogger(__name__)

__all__ = ["to_shapely"]


def resolve_polyline(v):
    if isinstance(v, Arc):
        return v.flattening(DEFAULT_STEP_SIZE)

    elif isinstance(v, Face3d):
        return v.wcs_vertices(True)

    return v.points()


def to_shapely(
    entity: DXFEntity,
    m: Matrix44 = None,
    step_size: float = DEFAULT_STEP_SIZE,
    precision: float = DEFAULT_PRECISION,
) -> Generator[
    Tuple[
        shapely.geometry.base.BaseGeometry, Union[DXFEntity, BlockInsertion, FailCase]
    ],
    None,
    None,
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

    elif (
        isinstance(entity, Polyline)
        and not (entity.is_3d_polyline or entity.is_2d_polyline)
        and entity.is_closed
    ):
        poly = shapely.Polygon((p.x, p.y) for p in entity.points())

        if True:
            poly = clean_shape(poly)
        yield poly, entity
    elif isinstance(entity, Polyline) and entity.is_poly_face_mesh:
        a = []
        for v in entity.virtual_entities():
            h = []
            for p in resolve_polyline(v):
                h.append((p.x, p.y))
            a.append(shapely.LineString(h))
        poly = shapely.multilinestrings(a)

        if True:
            poly = clean_shape(poly)

        yield poly, entity

    elif isinstance(entity, ImageBase):
        yield shapely.LineString((v.x, v.y) for v in entity.boundary_path), entity

    elif isinstance(entity, Viewport):
        if False:
            for ent in recursive_decompose((entity,)):
                yield from to_shapely(ent, m)

        # entity.dxf.paperspace TODO: LOOK THIS UP
        # entity.clipping_rect_corners()

        if False:
            vec3 = entity.dxf.center
            width = entity.dxf.width
            height = entity.dxf.height

            yield shapely.Point(
                vec3.x,
                vec3.y,
                # , vec3.z
            ), entity
        else:
            (min_x, min_y, max_x, max_y) = entity.get_modelspace_limits()
            # (-71.605931530016, -0.7866669825158965, 491.60594764232457, 297.7866552316861)

            yield shapely.Polygon(
                (
                    (min_x, min_y),
                    (max_x, min_y),
                    (max_x, max_y),
                    (min_x, max_y),
                    (min_x, min_y),
                )
            ), entity

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
                if True:
                    logger.error(e)

                if False:
                    raise e

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
