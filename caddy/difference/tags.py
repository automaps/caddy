from difflib import SequenceMatcher
from typing import Dict, Iterable, Iterator, Optional

from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import DXFTag

__all__ = ["tags_difference", "tag_two_way_difference"]

from caddy.ezdxf_utilities import round_tags, OpCode, Operation, convert_opcodes


def tags_difference(
    a: Tags, b: Tags, ndigits: Optional[int] = None
) -> Iterator[Operation]:
    if ndigits is not None:
        a = Tags(round_tags(a, ndigits))
        b = Tags(round_tags(b, ndigits))

    # SequenceMatcher https://docs.python.org/3/library/difflib.html

    return convert_opcodes(SequenceMatcher(a=a, b=b).get_opcodes())


def tag_two_way_difference(a: Tags, b: Tags, operations: Iterable[Operation]) -> Dict:
    t1: DXFTag
    t2: DXFTag

    tag_level_res = {"insert": {}, "replace": {}, "delete": {}}

    for op in operations:
        if op.opcode == OpCode.insert:
            for t2 in b[op.j1 : op.j2]:
                tag_level_res["insert"][f"{op.i1}:{op.i2}"] = t2

        elif op.opcode == OpCode.replace:
            from_ = {}
            for index, t1 in enumerate(a[op.i1 : op.i2], op.i1):
                from_[index] = t1

            to_ = {}
            for index, t2 in enumerate(b[op.j1 : op.j2], op.j1):
                to_[index] = t2

            tag_level_res["replace"][f"{op.i1}:{op.i2},{op.j1}:{op.j2}"] = (from_, to_)

        elif op.opcode == OpCode.delete:
            for index, t1 in enumerate(a[op.i1 : op.i2], op.i1):
                tag_level_res["delete"][index] = t1

    return tag_level_res
