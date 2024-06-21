from pathlib import Path

from caddy.to_gpkg import export_to_gpkg

if __name__ == "__main__":
    export_to_gpkg(Path.home() / "Downloads" / "dxfs" / "Frb1_2-M_Aug2022.dxf")
