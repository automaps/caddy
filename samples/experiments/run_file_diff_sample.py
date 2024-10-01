import sys
from pathlib import Path
from typing import Tuple

import pandas
from ezdxf.lldxf.tags import Tags
from ezdxf.tools.difftags import diff_tags, print_diff
from ezdxf.tools.rawloader import raw_structure_loader
from warg import ensure_existence

from caddy.difference import get_entity_differences
from caddy.difference.blocks import get_block_differences
from caddy.ezdxf_utilities import get_matched_tag_based_on_entity_handle


def get_entities(doc1, doc2, handle: str) -> Tuple[Tags, Tags]:
    a = get_matched_tag_based_on_entity_handle(doc1["ENTITIES"], handle)
    b = get_matched_tag_based_on_entity_handle(doc2["ENTITIES"], handle)
    if a is None or b is None:
        raise ValueError(f"Entity #{handle} not present in both files")
    return a, b


def main(filename1: str, filename2: str, handle: str):
    doc1 = raw_structure_loader(filename1)
    doc2 = raw_structure_loader(filename2)
    try:
        a, b = get_entities(doc1, doc2, handle)
    except ValueError as e:
        print(str(e))
        sys.exit(1)
    print_diff(a, b, diff_tags(a, b, ndigits=6))


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
