try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum

__all__ = ["DxfSection"]


class DxfSection(StrEnum):
    header = "HEADER"
    classes = "CLASSES"
    tables = "TABLES"
    blocks = "BLOCKS"
    entities = "ENTITIES"
    objects = "OBJECTS"
    thumbnailimage = "THUMBNAILIMAGE"
    acdsdata = "ACDSDATA"
    end_of_file = "END OF FILE"
