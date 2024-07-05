import logging
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import ezdxf
import shapely
from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.lldxf.tags import Tags
from ezdxf.tools.rawloader import raw_structure_loader
from jord.shapely_utilities import dilate

from .conversion import to_shapely
from .helpers import OpCode, tag_two_way_difference, tags_difference

logger = logging.getLogger(__name__)

__all__ = [
    "get_handle",
    "section_two_way_difference",
    "entity_tags",
    "get_entity_difference",
]


def get_handle(tags: Tags) -> str:
    try:
        return tags.get_handle()
    except ValueError:
        return "0"


def section_two_way_difference(
    original_section: List[Union[Tags, ExtendedTags]],
    new_section: List[Union[Tags, ExtendedTags]],
    precision: int = 6,
) -> Dict:
    entity_level_result = {"created": [], "modified": [], "deleted": []}

    for original_tags in original_section:
        entity_handle = get_handle(original_tags)

        if entity_handle is None or entity_handle == "0":
            continue

        new_entity_tags = entity_tags(new_section, entity_handle)

        if new_entity_tags is None:
            logger.info(f"entity handle #{entity_handle} not found in new file")
            entity_level_result["deleted"] = entity_handle
            continue

        compiled_original_tags = Tags(tag_compiler(iter(original_tags)))

        tag_level_difference = list(
            tags_difference(new_entity_tags, compiled_original_tags, ndigits=precision)
        )
        has_tag_level_difference = any(
            op.opcode != OpCode.equal for op in tag_level_difference
        )
        if has_tag_level_difference:
            entity_level_result["modified"].append(
                (
                    entity_handle,
                    tag_two_way_difference(
                        compiled_original_tags, new_entity_tags, tag_level_difference
                    ),
                )
            )

    for new_tags in new_section:
        entity_handle = get_handle(new_tags)
        old_entity_tags = entity_tags(new_section, entity_handle)

        if old_entity_tags is None:
            logger.info(
                f"entity handle #{entity_handle} not found in the original file"
            )
            entity_level_result["created"] = entity_handle
            continue

    return entity_level_result


def raw_dxf_difference(original: Path, new: Path) -> Dict:
    original_document = raw_structure_loader(str(original))
    new_document = raw_structure_loader(str(new))
    for section in ["TABLES", "BLOCKS", "ENTITIES", "OBJECTS"]:
        yield {
            section: section_two_way_difference(
                original_document[section], new_document[section]
            )
        }


def entity_tags(entities: Iterable[Tags], handle: str) -> Optional[Tags]:
    for e in entities:
        if get_handle(e) == handle:
            return Tags(tag_compiler(iter(e)))

    return None


def strip_z_coord(l):
    return shapely.ops.transform(lambda x, y, z=None: (x, y), l)


def get_entity_difference(*pair) -> Dict:
    out = defaultdict(dict)
    source_dxf = ezdxf.readfile(pair[0])
    target_dxf = ezdxf.readfile(pair[1])

    buffer_size = 10

    for d in raw_dxf_difference(*pair):
        k, v = next(iter(d.items()))
        if k == "ENTITIES":
            created, modified, deleted = v["created"], v["modified"], v["deleted"]

            for handle in created:
                target_entity = target_dxf.entitydb.get(handle)
                for g in to_shapely(target_entity):
                    out[handle]["added entity"] = g

            for handle in deleted:
                source_entity = source_dxf.entitydb.get(handle)
                for g in to_shapely(source_entity):
                    out[handle]["deleted entity"] = g

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

                    src_geom: shapely.geometry.base.BaseGeometry = strip_z_coord(
                        src_geom[0]
                    )
                    tgt_geom: shapely.geometry.base.BaseGeometry = strip_z_coord(
                        tgt_geom[0]
                    )

                    if True:
                        if isinstance(src_geom, shapely.Point):
                            out[handle]["src point"] = src_geom
                            out[handle]["tgt point"] = tgt_geom
                        else:
                            added = src_geom.difference(tgt_geom)
                            remaining = src_geom.intersection(tgt_geom)
                            removed = tgt_geom.difference(src_geom)

                            if not added.is_empty:
                                out[handle]["added geometry"] = added
                            if not added.is_empty:
                                out[handle]["remaining geometry"] = remaining
                            if not added.is_empty:
                                out[handle]["removed geometry"] = removed

                    out[handle]["diffbuffer"] = dilate(
                        shapely.unary_union((src_geom, tgt_geom)), buffer_size
                    )  # Buffer

                if True:
                    out[handle]["added tags"] = insert
                    out[handle]["deleted tags"] = delete
                    out[handle]["replaced tags"] = replace

    return dict(**out)
