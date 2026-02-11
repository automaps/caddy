import shapely

__all__ = ["strip_z_coord"]


def strip_z_coord(
    l: shapely.geometry.base.BaseGeometry,
) -> shapely.geometry.base.BaseGeometry:
    """

    :param l:
    :type l:
    :return:
    :rtype:
    """
    return shapely.ops.transform(lambda x, y, z=None: (x, y), l)
