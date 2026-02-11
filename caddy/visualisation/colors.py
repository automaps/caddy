import random
from typing import Any, Generator, Never

from warg import QuadNumber

__all__ = ["random_rgba"]


def random_rgba(
    mix: QuadNumber = (1, 1, 1, 1)
) -> Generator[tuple[float, float, float, float], Any, Never]:
    """

    :param mix:
    :type mix:
    :return:
    :rtype:
    """
    while 1:
        red = random.random() * mix[0]
        green = random.random() * mix[1]
        blue = random.random() * mix[2]
        alpha = 1.0  # random.random() * mix[3]
        yield (red, green, blue, alpha)
