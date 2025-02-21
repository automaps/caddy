from collections import defaultdict
from pathlib import Path
from typing import Optional

from ezdxf.entities import Insert, MText, Text
from geopandas import GeoDataFrame

from caddy.exporting import extract_shaped_dxf_entities, logger

LAYER_WISE = False


def export_to(
    dxf_path: Path, out_path: Optional[Path] = None, driver: str = "GPKG"
) -> None:
    if out_path is None:
        out_path = Path(dxf_path).with_suffix(".gpkg")

    dxf_entities = extract_shaped_dxf_entities(dxf_path)

    logger.warning(f"Exporting {dxf_path} -> {out_path}")

    if LAYER_WISE:
        for l, ges in dict(dxf_entities).items():
            extras = defaultdict(list)

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

            gdf = GeoDataFrame({"geometry": g, **extras})
            # gdf.crs = 'EPSG:4326'
            # gdf.to_file(str(out_path), driver=driver, layer=l)
            if True:
                gdf.to_file(str(out_path), driver=driver)
            else:
                gdf.to_file(
                    str(out_path.with_suffix(".sqlite")),
                    driver="SQLite",
                    spatialite=True,
                    layer=l,
                )
    else:
        extras = defaultdict(list)
        for l, ges in dict(dxf_entities).items():
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

        gdf = GeoDataFrame(extras, geometry="geometry")

        # gdf.crs = 'EPSG:4326'
        if True:
            gdf.to_file(str(out_path), driver=driver)
        else:
            gdf.to_file(
                str(out_path.with_suffix(".sqlite")),
                driver="SQLite",
                spatialite=True,
            )

    logger.warning(f"Wrote {out_path}")
