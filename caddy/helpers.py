#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations

import enum
import random
from difflib import SequenceMatcher
from typing import Dict, Iterable, Iterator, List, NamedTuple, Optional, Tuple

import shapely
from ezdxf.lldxf.tags import Tags
from ezdxf.lldxf.types import DXFTag, DXFVertex

__all__ = [
    "tags_difference",
    "tag_two_way_difference",
    "OpCode",
    "convert_opcodes",
    "round_tags",
    "get_transformation",
    "plot_shapely_geometry",
    "random_rgba",
    "CONVERT",
]

from numpy import cos, radians, sin
from shapely import plotting
from warg import QuadNumber

from caddy.exporting import BlockPointInsert

# https://docs.python.org/3/library/difflib.html


class OpCode(enum.Enum):
    replace = enum.auto()
    delete = enum.auto()
    insert = enum.auto()
    equal = enum.auto()


class Operation(NamedTuple):
    opcode: OpCode
    i1: int
    i2: int
    j1: int
    j2: int


CONVERT = {
    "replace": OpCode.replace,
    "delete": OpCode.delete,
    "insert": OpCode.insert,
    "equal": OpCode.equal,
}


def convert_opcodes(
    opcodes: Iterable[Tuple[str, int, int, int, int]]
) -> Iterator[Operation]:
    for tag, i1, i2, j1, j2 in opcodes:
        yield Operation(CONVERT[tag], i1, i2, j1, j2)


def round_tags(tags: Tags, ndigits: int) -> Iterator[DXFTag]:
    for tag in tags:
        if isinstance(tag, DXFVertex):
            yield DXFVertex(tag.code, (round(d, ndigits) for d in tag.value))
        elif isinstance(tag.value, float):
            yield DXFTag(tag.code, round(tag.value, ndigits))  # type: ignore
        else:
            yield tag


def tags_difference(
    a: Tags, b: Tags, ndigits: Optional[int] = None
) -> Iterator[Operation]:
    if ndigits is not None:
        a = Tags(round_tags(a, ndigits))
        b = Tags(round_tags(b, ndigits))

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


def get_transformation(insertion_point: BlockPointInsert) -> List[float]:
    if insertion_point.matrix44:
        m = insertion_point.matrix44.get_2d_transformation()  # row wise
        return [m[0], m[3], m[1], m[4], m[6], m[7]]

    angle = radians(insertion_point.rotation)
    cos_angle = cos(angle)
    sin_angle = sin(angle)

    return [
        insertion_point.x_scale * cos_angle,
        insertion_point.y_scale * -sin_angle,
        insertion_point.x_scale * sin_angle,
        insertion_point.y_scale * cos_angle,
        insertion_point.point.x,
        insertion_point.point.y,
    ]


def random_rgba(mix: QuadNumber = (1, 1, 1, 1)) -> QuadNumber:
    while 1:
        red = random.random() * mix[0]
        green = random.random() * mix[1]
        blue = random.random() * mix[2]
        alpha = 1.0  # random.random() * mix[3]
        yield (red, green, blue, alpha)


def plot_shapely_geometry(
    geom: shapely.geometry.base.BaseGeometry, color: QuadNumber
) -> None:
    if isinstance(geom, shapely.GeometryCollection):
        for g in geom.geoms:
            plot_shapely_geometry(g, color)
    elif isinstance(geom, (shapely.LineString, shapely.MultiLineString)):
        plotting.plot_line(geom, add_points=False, color=color)
    elif isinstance(geom, (shapely.Point, shapely.MultiPoint)):
        plotting.plot_points(geom, add_points=False, color=color)
    else:
        plotting.plot_polygon(geom, add_points=False, color=color)
