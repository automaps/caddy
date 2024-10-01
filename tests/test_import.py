from pathlib import Path

from warg import ensure_in_sys_path

ensure_in_sys_path(Path(__file__).parent.parent)


def test_import_package():
    import caddy
    from caddy import conversion
    from caddy import difference
    from caddy import exporting
    from caddy import ezdxf_utilities
    from caddy import shapely_utilities
    from caddy import visualisation
    from caddy import model

    print(caddy.__doc__)
    print(conversion.__doc__)
    print(difference.__doc__)
    print(exporting.__doc__)
    print(ezdxf_utilities.__doc__)
    print(shapely_utilities.__doc__)
    print(model.__doc__)
    print(visualisation.__doc__)


def test_math():
    assert 1 + 1 == 2
