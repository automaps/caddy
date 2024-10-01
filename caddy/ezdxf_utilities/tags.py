from typing import Iterable, Iterator, Optional

from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import DXFTag, DXFVertex

from .handles import get_handle

__all__ = ["get_matched_tag_based_on_entity_handle", "round_tags"]


def get_matched_tag_based_on_entity_handle(
    entities: Iterable[Tags], old_handle: str
) -> Optional[Tags]:
    for e in entities:
        new_handle = get_handle(e)
        if new_handle == old_handle:
            return Tags(tag_compiler(iter(e)))

    return None


def round_tags(tags: Tags, ndigits: int) -> Iterator[DXFTag]:
    for tag in tags:
        if isinstance(tag, DXFVertex):
            yield DXFVertex(tag.code, (round(d, ndigits) for d in tag.value))
        elif isinstance(tag.value, float):
            yield DXFTag(tag.code, round(tag.value, ndigits))  # type: ignore
        else:
            yield tag
