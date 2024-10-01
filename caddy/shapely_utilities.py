#  Copyright (c) 2021-2022, Manfred Moitzi
#  License: MIT License
from __future__ import annotations

import shapely

__all__ = []


# https://docs.python.org/3/library/difflib.html


def strip_z_coord(l):
    return shapely.ops.transform(lambda x, y, z=None: (x, y), l)
