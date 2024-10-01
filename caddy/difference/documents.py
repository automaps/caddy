import logging
from pathlib import Path
from typing import Dict

from ezdxf.tools.rawloader import raw_structure_loader

from caddy.ezdxf_utilities import DxfSection
from .sections import section_two_way_difference

logger = logging.getLogger(__name__)

__all__ = ["document_differences"]


def document_differences(
    left_document_path: Path, right_document_path: Path, **kwargs
) -> tuple[DxfSection, Dict]:
    original_document = raw_structure_loader(str(left_document_path))
    new_document = raw_structure_loader(str(right_document_path))
    for section in DxfSection:
        if section.value in original_document:
            if section.value in new_document:
                yield (
                    section,
                    section_two_way_difference(
                        original_document[section.value],
                        new_document[section.value],
                        **kwargs,
                    ),
                )
            else:
                logger.warning(f"{section=} was not found in {right_document_path=}")
        else:
            logger.warning(f"{section=} was not found in {left_document_path=}")
