from collections import defaultdict
from pathlib import Path
from typing import Dict

import ezdxf

from caddy.ezdxf_utilities import DxfSection
from .documents import document_differences

__all__ = ["get_block_differences"]


def get_block_differences(
    left_file_path: Path, right_file_path: Path, diff_buffer_dilation_size: float = 10
) -> Dict:
    out = defaultdict(dict)

    source_dxf = ezdxf.readfile(left_file_path)
    target_dxf = ezdxf.readfile(right_file_path)

    for section, two_diff_dict in document_differences(
        left_file_path, right_file_path, sections=(DxfSection.blocks,)
    ):
        if section == DxfSection.blocks:
            ...

    raise NotImplementedError("TODO: FINISH THIS!")
