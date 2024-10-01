from typing import List

from numpy import cos, radians, sin

from caddy.exporting import BlockPointInsert

__all__ = ["get_transformation"]


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
