from typing import Iterable, Iterator, Optional

from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import DXFTag, DXFVertex

from .handles import get_handle

__all__ = ["get_matched_tag_based_on_entity_handle", "round_tags"]


def get_matched_tag_based_on_entity_handle(
    entities: Iterable[Tags], query_handle: str
) -> Optional[Tags]:
    for entity in entities:
        result_handle = get_handle(entity)
        if result_handle is not None:
            if result_handle != "0":
                if result_handle == query_handle:
                    return Tags(tag_compiler(iter(entity)))

    return None


def round_tags(tags: Tags, ndigits: int) -> Iterator[DXFTag]:
    for tag in tags:
        if isinstance(tag, DXFVertex):
            yield DXFVertex(tag.code, (round(d, ndigits) for d in tag.value))
        elif isinstance(tag.value, float):
            yield DXFTag(tag.code, round(tag.value, ndigits))  # type: ignore
        else:
            yield tag
