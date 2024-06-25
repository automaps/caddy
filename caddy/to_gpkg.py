from collections import OrderedDict, defaultdict
from pathlib import Path

import ezdxf
import shapely
from ezdxf.math import Matrix44
from geopandas import GeoDataFrame

__all__ = ["export_to_gpkg"]

from jord.shapely_utilities.base import clean_shape
from jord.shapely_utilities.polygons import ensure_cw_poly, is_polygonal

from ezdxf.entities import DXFEntity, DXFGraphic, Insert, MText, Text
from .conversion import to_shapely


def export_to_gpkg(dxf_path: Path, out_path: Path, driver="GPKG") -> None:
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
                cleaned = clean_shape(g)
                if False:
                    if is_polygonal(cleaned):
                        cleaned = ensure_cw_poly(cleaned)
                geoms[e.dxf.layer].append((cleaned, e))

    for l, ges in dict(geoms).items():
        extras = defaultdict(list)

        g, e = zip(*ges)

        for e in e:
            if isinstance(e, (MText, Text)):
                if hasattr(e, "plain_text"):
                    extras["text"].append(e.plain_text())
                else:
                    extras["text"].append(e.dxf.text)
            else:
                extras["text"].append("")

        gdf = GeoDataFrame({"geometry": g, **extras})
        # gdf.crs = 'EPSG:4326'
        gdf.to_file(str(out_path), driver=driver, layer=l)
