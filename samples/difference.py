from pathlib import Path
from pprint import pprint

from caddy.difference import raw_dxf_difference

if __name__ == "__main__":

  for pair in (
      (Path.home() / 'Downloads' / 'dxfs' / 'Frb1_2-M_Aug2022.dxf',
       Path.home() / 'Downloads' / 'dxfs' / 'Frb1_2-M_Jan2024.dxf'),
      (Path.home() / 'Downloads' / 'dxfs' / '132173_22_20240106-003031.dxf',
       Path.home() / 'Downloads' / 'dxfs' / '132173_22_20240327-023017.dxf'),
      (Path.home() / 'Downloads' / 'dxfs' / 'Frb1_K-M_Aug2022.dxf',
       Path.home() / 'Downloads' / 'dxfs' / 'Frb1_K-M_Jan2024.dxf'),
  ):
    for d in raw_dxf_difference(*pair):
      k, v = next(iter(d.items()))
      if k == 'ENTITIES':
        pprint(v)
    break
