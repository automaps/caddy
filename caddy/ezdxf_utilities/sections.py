from enum import Enum

__all__ = ["DxfSection"]


class DxfSection(Enum):
    # header = 'HEADER'
    # classes = 'CLASSES'
    # tables="TABLES"
    # blocks="BLOCKS"
    entities = "ENTITIES"
    objects = "OBJECTS"
    thumbnailimage = "THUMBNAILIMAGE"
    acdsdata = "ACDSDATA"
    end_of_file = "END OF FILE"
