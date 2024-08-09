from pathlib import Path

import ezdxf
import shapely

from caddy.difference import raw_dxf_difference
from caddy.exporting import to_shapely

if __name__ == "__main__":
    for pair in (
        (
            Path.home() / "Downloads" / "dxfs" / "Frb1_2-M_Aug2022.dxf",
            Path.home() / "Downloads" / "dxfs" / "Frb1_2-M_Jan2024.dxf",
        ),
        (
            Path.home() / "Downloads" / "dxfs" / "Frb1_K-M_Aug2022.dxf",
            Path.home() / "Downloads" / "dxfs" / "Frb1_K-M_Jan2024.dxf",
        ),
        (
            Path.home() / "Downloads" / "dxfs" / "132173_22_20240106-003031.dxf",
            Path.home() / "Downloads" / "dxfs" / "132173_22_20240327-023017.dxf",
        ),
    ):
        source_dxf = ezdxf.readfile(pair[0])
        target_dxf = ezdxf.readfile(pair[1])

        for d in raw_dxf_difference(*pair):
            k, v = next(iter(d.items()))
            if k == "ENTITIES":
                created, modified, deleted = v["created"], v["modified"], v["deleted"]

                for handle in created:
                    target_entity = target_dxf.entitydb.get(handle)
                    for g in to_shapely(target_entity):
                        print("added entity", g.wkt)

                for handle in deleted:
                    source_entity = source_dxf.entitydb.get(handle)
                    for g in to_shapely(source_entity):
                        print("deleted entity", g.wkt)

                for m in modified:
                    handle, operations = m
                    delete, insert, replace = (
                        operations["delete"],
                        operations["insert"],
                        operations["replace"],
                    )

                    source_entity = source_dxf.entitydb.get(handle)
                    target_entity = target_dxf.entitydb.get(handle)

                    for src_geom in to_shapely(source_entity):
                        tgt_geom = next(iter(to_shapely(target_entity)))

                        src_geom: shapely.geometry.base.BaseGeometry = src_geom[0]
                        tgt_geom: shapely.geometry.base.BaseGeometry = tgt_geom[0]

                        if isinstance(src_geom, shapely.Point):
                            print("src point", src_geom.wkt)
                            print("tgt point", tgt_geom.wkt)
                        else:
                            added = src_geom.difference(tgt_geom)
                            remaining = src_geom.intersection(tgt_geom)
                            removed = tgt_geom.difference(src_geom)

                            print("added geometry", added.wkt)
                            print("remaining geometry", remaining.wkt)
                            print("removed geometry", removed.wkt)

                    print("added tags", insert)
                    print("deleted tags", delete)
                    print("replaced tags", replace)
        break
