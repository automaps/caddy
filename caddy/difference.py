import logging
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

from ezdxf.lldxf.extendedtags import ExtendedTags
from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.lldxf.tags import Tags
from ezdxf.tools.rawloader import raw_structure_loader

from caddy.helpers import OpCode, tag_two_way_difference, tags_difference

logger = logging.getLogger(__name__)


def get_handle(tags: Tags) -> str:
  try:
    return tags.get_handle()
  except ValueError:
    return "0"


def section_two_way_difference(original_section: List[Union[Tags, ExtendedTags]],
                               new_section: List[Union[Tags, ExtendedTags]],
                               precision: int = 6) -> Dict:
  entity_level_result = {'created': [], 'modified': [], 'deleted': []}

  for original_tags in original_section:
    entity_handle = get_handle(original_tags)

    if entity_handle is None or entity_handle == "0":
      continue

    new_entity_tags = entity_tags(new_section, entity_handle)

    if new_entity_tags is None:
      logger.info(f"entity handle #{entity_handle} not found in new file")
      entity_level_result['deleted'] = entity_handle
      continue

    compiled_original_tags = Tags(tag_compiler(iter(original_tags)))

    tag_level_difference = list(tags_difference(new_entity_tags, compiled_original_tags, ndigits=precision))
    has_tag_level_difference = any(op.opcode != OpCode.equal for op in tag_level_difference)
    if has_tag_level_difference:
      entity_level_result['modified'].append(
        tag_two_way_difference(compiled_original_tags, new_entity_tags, tag_level_difference))

  for new_tags in new_section:
    entity_handle = get_handle(new_tags)
    old_entity_tags = entity_tags(new_section, entity_handle)

    if old_entity_tags is None:
      logger.info(f"entity handle #{entity_handle} not found in the original file")
      entity_level_result['created'] = entity_handle
      continue

  return entity_level_result


def raw_dxf_difference(original: Path, new: Path) -> Dict:
  original_document = raw_structure_loader(str(original))
  new_document = raw_structure_loader(str(new))
  for section in ["TABLES", "BLOCKS", "ENTITIES", "OBJECTS"]:
    yield {
      section: section_two_way_difference(original_document[section], new_document[section])
    }


def entity_tags(entities: Iterable[Tags], handle: str) -> Optional[Tags]:
  for e in entities:
    if get_handle(e) == handle:
      return Tags(tag_compiler(iter(e)))

  return None
