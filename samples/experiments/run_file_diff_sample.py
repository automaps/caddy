import sys
from pathlib import Path
from typing import Iterable, Optional, Tuple

import pandas
from ezdxf.lldxf.tagger import tag_compiler
from ezdxf.lldxf.tags import Tags
from ezdxf.tools.difftags import diff_tags, print_diff
from ezdxf.tools.rawloader import raw_structure_loader
from warg import ensure_existence

from caddy.difference import get_entity_difference


def entity_tags(entities: Iterable[Tags], handle: str) -> Optional[Tags]:
    def get_handle(tags: Tags):
        try:
            return tags.get_handle()
        except ValueError:
            return "0"

    for e in entities:
        if get_handle(e) == handle:
            return Tags(tag_compiler(iter(e)))
    return None


def get_entities(doc1, doc2, handle: str) -> Tuple[Tags, Tags]:
    a = entity_tags(doc1["ENTITIES"], handle)
    b = entity_tags(doc2["ENTITIES"], handle)
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


def difference():
    dxf_base_dir = Path(r"C:\Users\chen\Downloads\dxfs")

    left, right = (
        dxf_base_dir / "Frb1_K-M_Aug2022.dxf",
        dxf_base_dir / "Frb1_K-M_Jan2024.dxf",
    )

    return_dict = get_entity_difference(left, right)

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
    difference()
