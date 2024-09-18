from pathlib import Path

from warg import ensure_in_sys_path

ensure_in_sys_path(Path(__file__).parent.parent)


def test_import_package():
    import caddy
    import caddy.conversion
    import caddy.difference
    import caddy.exporting
    import caddy.helpers

    print(caddy.__version__)
