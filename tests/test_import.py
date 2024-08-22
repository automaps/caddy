from pathlib import Path

from warg import ensure_in_sys_path

ensure_in_sys_path(Path(__file__).parent.parent)


def test_import_package():
    if True:
        import caddy

        print(caddy.__version__)


def test_math():
    assert 1 + 1 == 2
