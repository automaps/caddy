import logging
from pathlib import Path
from typing import Dict

from ezdxf.tools.rawloader import raw_structure_loader

from .sections import section_two_way_difference
from caddy.ezdxf_utilities import DxfSection

logger = logging.getLogger(__name__)

__all__ = []


def raw_dxf_difference(original: Path, new: Path, **kwargs) -> tuple[DxfSection, Dict]:
    original_document = raw_structure_loader(str(original))
    new_document = raw_structure_loader(str(new))
    for section in DxfSection:
        yield (
            section,
            section_two_way_difference(
                original_document[section.value], new_document[section.value], **kwargs
            ),
        )
