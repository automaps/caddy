import logging
from typing import List, Union, Dict

from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.lldxf.tags import Tags

from caddy.ezdxf_utilities import (
    get_handle,
    get_matched_tag_based_on_entity_handle,
    OpCode,
)
from .tags import tags_difference, tag_two_way_difference

logger = logging.getLogger(__name__)


def section_two_way_difference(
    original_section: List[Union[Tags, ExtendedTags]],
    new_section: List[Union[Tags, ExtendedTags]],
    precision: int = 6,
) -> Dict:
    entity_level_result = {"created": [], "modified": [], "deleted": []}

    for original_tags in original_section:
        old_entity_handle = get_handle(original_tags)

        if old_entity_handle is None or old_entity_handle == "0":
            continue

        new_entity_tags = get_matched_tag_based_on_entity_handle(
            new_section, old_entity_handle
        )

        if new_entity_tags is None:
            logger.info(f"entity handle #{old_entity_handle} not found in new file")
            entity_level_result["deleted"] = old_entity_handle
        else:
            compiled_original_tags = Tags(tag_compiler(iter(original_tags)))

            tag_level_difference = list(
                tags_difference(
                    new_entity_tags, compiled_original_tags, ndigits=precision
                )
            )
            has_tag_level_difference = any(
                op.opcode != OpCode.equal for op in tag_level_difference
            )

            if has_tag_level_difference:
                entity_level_result["modified"].append(
                    (
                        old_entity_handle,
                        tag_two_way_difference(
                            compiled_original_tags,
                            new_entity_tags,
                            tag_level_difference,
                        ),
                    )
                )

    for new_tags in new_section:
        new_entity_handle = get_handle(new_tags)
        new_entity_tags = get_matched_tag_based_on_entity_handle(
            new_section, new_entity_handle
        )

        if new_entity_tags is None:
            logger.info(
                f"entity handle #{new_entity_handle} not found in the original file"
            )
            entity_level_result["created"] = new_entity_handle

    return entity_level_result
