from collections import OrderedDict, defaultdict
from pathlib import Path

import ezdxf
from ezdxf.math import Matrix44
from geopandas import GeoDataFrame

__all__ = ["export_to_gpkg"]

from .conversion import to_shapely


def export_to_gpkg(dxf_path: Path, out_path: Path) -> None:
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
        gdf.to_file(str(out_path), driver=driver, layer=l)
