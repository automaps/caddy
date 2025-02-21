import logging
from pathlib import Path

from caddy.exporting import export_to

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    # export_to(Path.home() / "Downloads" / "dxfs" / "Frb1_2-M_Aug2022.dxf")
    # export_to(Path.home() / "Downloads" / "dxfs" / "Frb1_K-M_Aug2022.dxf")
    # export_to(Path.home() / "Downloads" / "dxfs" / "132173_22_20240106-003031.dxf")

    # export_to(Path.home() / "Downloads" / "5215-01-kl-fur.dxf")
    export_to(Path(__file__).parent.parent / "tests" / "fixtures" / "weird00.dxf")
