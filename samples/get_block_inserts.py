from pathlib import Path

from caddy.exporting import get_block_geoms

from pprint import pprint

if __name__ == "__main__":
    # get_block_geoms(Path.home() / "Downloads" / "dxfs" / "Frb1_2-M_Aug2022.dxf")
    pprint(get_block_geoms(Path.home() / "Downloads" / "dxfs" / "Frb1_K-M_Aug2022.dxf"))
    # get_block_geoms(Path.home() / "Downloads" / "dxfs" / "132173_22_20240106-003031.dxf")

    # get_block_geoms(Path.home() / "Downloads" / "5215-01-kl-fur.dxf")
