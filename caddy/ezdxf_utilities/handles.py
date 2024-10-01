from ezdxf.lldxf.tags import Tags

__all__ = ["get_handle"]


def get_handle(tags: Tags) -> str:
    try:
        return tags.get_handle()
    except ValueError:
        return "0"
