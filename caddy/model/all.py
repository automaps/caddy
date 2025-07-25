from dataclasses import dataclass

import shapely
from ezdxf.entities import DXFEntity, Insert
from ezdxf.layouts import BlockLayout

__all__ = ["FailCase", "BlockInsertion", "BlockPointInsert"]

from ezdxf.math import Matrix44


@dataclass
class BlockInsertion:
    block: BlockLayout
    insertion: Insert


@dataclass
class FailCase:
    entity: DXFEntity
    case: str


@dataclass
class BlockPointInsert:
    point: shapely.Point
    rotation: float
    x_scale: float
    y_scale: float
    z_scale: float
    matrix44: Matrix44
