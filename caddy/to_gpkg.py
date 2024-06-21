import logging
from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Iterable

import ezdxf
import shapely
from ezdxf.addons import geo
from ezdxf.entities import DXFEntity, DXFGraphic, Insert
from ezdxf.math import Matrix44
from ezdxf.query import EntityQuery
from geopandas import GeoDataFrame

TRANSFORM = False

logger = logging.getLogger(__name__)


def to_shapely(entity: DXFEntity, m, step_size=0.1):
    if isinstance(entity, Insert):
        entities: EntityQuery = entity.explode()
        # entities.groupby()
        for ent in entities:
            yield from to_shapely(ent, m)

        return

    elif isinstance(entity, (DXFGraphic, Iterable[DXFGraphic])):
        try:
            geo_proxy = geo.proxy(entity, distance=step_size, force_line_string=False)

            geo_proxy.places = None  # Infinite precision

            if TRANSFORM:
                # Transform DXF WCS coordinates into CRS coordinates:
                geo_proxy.wcs_to_crs(m)
                # Transform 2D map projection EPSG:3395 into globe (polar)
                # representation EPSG:4326
                geo_proxy.map_to_globe()

            geom = shapely.geometry.shape(geo_proxy)
            yield geom, entity

        except Exception as e:
            logger.info(entity)
            ...
    else:
        # logger.info(entity)
        ...


def export_to_gpkg(dxf_path: Path):
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

    geoms = defaultdict(list)
    for entity in msp.query("*"):
        for g, e in to_shapely(entity, m):
            if g:
                geoms[e.dxf.layer].append(g)

    driver = "GPKG"
    schema = {
        "geometry": "Polygon",
        "properties": OrderedDict(
            [
                ("dataType", "str"),
                ("fname", "str"),
                ("path", "str"),
                ("native_crs", "int"),
                ("lastmod", "str"),
            ]
        ),
    }

    for l, g in dict(geoms).items():
        gdf = GeoDataFrame({"geometry": g})
        # gdf.crs = 'EPSG:4326'
        gdf.to_file("out.gpkg", driver=driver, layer=l)
