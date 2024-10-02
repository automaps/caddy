from collections import defaultdict
from pathlib import Path
from typing import Dict

import ezdxf
import shapely
from jord.shapely_utilities import dilate

from caddy.conversion import to_shapely
from caddy.ezdxf_utilities import DxfSection
from caddy.shapely_utilities import strip_z_coord
from .documents import document_differences

__all__ = ["get_entity_differences"]


def get_entity_differences(
    left_file_path: Path, right_file_path: Path, diff_buffer_dilation_size: float = 10
) -> Dict:
    out = defaultdict(dict)

    source_dxf = ezdxf.readfile(left_file_path)
    target_dxf = ezdxf.readfile(right_file_path)

    for section, two_diff_dict in document_differences(
        left_file_path, right_file_path, sections=(DxfSection.entities,)
    ):
        if section == DxfSection.entities:
            created_entities, modified_entities, deleted_entities = (
                two_diff_dict["created"],
                two_diff_dict["modified"],
                two_diff_dict["deleted"],
            )

            for entity_handle in created_entities:
                for geometry, origin in to_shapely(
                    target_dxf.entitydb.get(entity_handle)
                ):
                    out[entity_handle]["new geometry"] = geometry
                    out[entity_handle]["diffbuffer"] = geometry
                    out[entity_handle]["difftype"] = "new"

            for entity_handle in deleted_entities:
                for geometry, origin in to_shapely(
                    source_dxf.entitydb.get(entity_handle)
                ):
                    out[entity_handle]["deleted geometry"] = geometry
                    out[entity_handle]["diffbuffer"] = geometry
                    out[entity_handle]["difftype"] = "deleted"

            for entity_handle, operations in modified_entities:
                deleted_tags, inserted_tags, replaced_tags = (
                    operations["delete"],
                    operations["insert"],
                    operations["replace"],
                )

                old_geometries = to_shapely(source_dxf.entitydb.get(entity_handle))
                new_geometries = to_shapely(target_dxf.entitydb.get(entity_handle))

                for (src_geom, src_origin), (tgt_geom, tgt_origin) in zip(
                    old_geometries, new_geometries, strict=True
                ):
                    src_geom = strip_z_coord(src_geom)
                    tgt_geom = strip_z_coord(tgt_geom)

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
                        shapely.unary_union((src_geom, tgt_geom)),
                        distance=diff_buffer_dilation_size,
                    )  # Buffer
                    out[entity_handle]["difftype"] = "modified"

                if True:
                    out[entity_handle]["added tags"] = inserted_tags
                    out[entity_handle]["deleted tags"] = deleted_tags
                    out[entity_handle]["replaced tags"] = replaced_tags

    return dict(**out)
