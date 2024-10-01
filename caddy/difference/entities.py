from collections import defaultdict
from typing import Dict

import ezdxf
import shapely
from jord.shapely_utilities import dilate

from caddy.conversion import to_shapely
from caddy.ezdxf_utilities import DxfSection
from .file_level_diff import raw_dxf_difference

__all__ = ["get_entity_difference"]

from ..shapely_utilities import strip_z_coord


def get_entity_difference(left, right) -> Dict:
    out = defaultdict(dict)
    source_dxf = ezdxf.readfile(left)
    target_dxf = ezdxf.readfile(right)

    buffer_size = 10

    for section, two_diff_dict in raw_dxf_difference(left, right):
        if section == DxfSection.entities:
            created_entities, modified_entities, deleted_entities = (
                two_diff_dict["created"],
                two_diff_dict["modified"],
                two_diff_dict["deleted"],
            )

            for entity_handle in created_entities:
                created_geometries = to_shapely(target_dxf.entitydb.get(entity_handle))
                assert len(created_geometries)
                for geometry in created_geometries:
                    out[entity_handle]["added geometry"] = geometry

            for entity_handle in deleted_entities:
                deleted_geometries = to_shapely(source_dxf.entitydb.get(entity_handle))
                for geometry in deleted_geometries:
                    out[entity_handle]["deleted geometry"] = geometry

            for entity_handle, operations in modified_entities:
                deleted_tags, inserted_tags, replaced_tags = (
                    operations["delete"],
                    operations["insert"],
                    operations["replace"],
                )

                old_geometries = to_shapely(source_dxf.entitydb.get(entity_handle))
                assert len(list(old_geometries))
                for src_geom in old_geometries:
                    new_geometries = to_shapely(target_dxf.entitydb.get(entity_handle))
                    assert len(new_geometries) == 1, f"{new_geometries=}"

                    tgt_geom = next(iter(new_geometries))

                    assert len(src_geom) == 1
                    assert len(tgt_geom) == 1

                    src_geom: shapely.geometry.base.BaseGeometry = strip_z_coord(
                        src_geom[0]
                    )
                    tgt_geom: shapely.geometry.base.BaseGeometry = strip_z_coord(
                        tgt_geom[0]
                    )

                    if True:
                        if isinstance(src_geom, shapely.Point):
                            out[entity_handle]["src point"] = src_geom
                            out[entity_handle]["tgt point"] = tgt_geom
                        else:
                            added = src_geom.difference(tgt_geom)
                            remaining = src_geom.intersection(tgt_geom)
                            removed = tgt_geom.difference(src_geom)

                            if not added.is_empty:
                                out[entity_handle]["added geometry"] = added
                            if not added.is_empty:
                                out[entity_handle]["remaining geometry"] = remaining
                            if not added.is_empty:
                                out[entity_handle]["removed geometry"] = removed

                    out[entity_handle]["diffbuffer"] = dilate(
                        shapely.unary_union((src_geom, tgt_geom)), buffer_size
                    )  # Buffer

                if True:
                    out[entity_handle]["added tags"] = inserted_tags
                    out[entity_handle]["deleted tags"] = deleted_tags
                    out[entity_handle]["replaced tags"] = replaced_tags

    return dict(**out)
