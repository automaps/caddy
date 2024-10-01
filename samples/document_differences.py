from pathlib import Path

import pandas
from warg import ensure_existence

from caddy.difference import get_entity_differences
from caddy.difference.blocks import get_block_differences


def compute_entity_difference():
    dxf_base_dir = Path(r"C:\Users\chen\Downloads\dxfs")

    left, right = (
        dxf_base_dir / "Frb1_K-M_Aug2022.dxf",
        dxf_base_dir / "Frb1_K-M_Jan2024.dxf",
    )

    return_dict = get_entity_differences(left, right)

    dataframe = pandas.DataFrame(return_dict)
    df = dataframe.T
    df = df.reset_index()
    df = df.rename(columns={"diffbuffer": "wkt", "index": "entity_handle"})

    data_output_path = ensure_existence(dxf_base_dir / "out")
    df.to_csv(
        data_output_path / f"difference_caddy.csv",
        index=False,
    )


def compute_block_difference():
    dxf_base_dir = Path(r"C:\Users\chen\Downloads\dxfs")

    left, right = (
        dxf_base_dir / "Frb1_K-M_Aug2022.dxf",
        dxf_base_dir / "Frb1_K-M_Jan2024.dxf",
    )

    return_dict = get_block_differences(left, right)

    dataframe = pandas.DataFrame(return_dict)
    df = dataframe.T
    df = df.reset_index()
    df = df.rename(columns={"diffbuffer": "wkt", "index": "entity_handle"})

    data_output_path = ensure_existence(dxf_base_dir / "out")
    df.to_csv(
        data_output_path / f"difference_caddy.csv",
        index=False,
    )


if __name__ == "__main__":
    compute_block_difference()
