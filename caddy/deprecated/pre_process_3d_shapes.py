from pathlib import Path

import ezdxf
from ezdxf.acis import api as acis
from ezdxf.entities import Body


def method_name(e, msp_out):
    print(f"Processing {e}")

    assert isinstance(e, Body)

    if e.has_binary_data:
        data = e.sab

        # data = acis.dump_sab_as_text(data)
        # data = BinaryAcisData(e.sab, 'asf', handle=e.dxf.handle).lines
    else:
        data = e.sat

    if data:
        for body in acis.load(data):
            for mesh in acis.mesh_from_body(body):
                mesh.render_mesh(msp_out)

            print(f"{str(e)} - face link structure:")

            dbg = acis.AcisDebugger(body)

            for shell in dbg.filter_type("shell"):
                print("\n".join(dbg.face_link_structure(shell.face, 2)))

                vertices = list(dbg.filter_type("vertex"))

                print(
                    f"\nThe shell has {len(vertices)} unique vertices.\n"
                    f"Each face has one loop."
                )
                print("Loop vertices:")

                for face in shell.faces():
                    print(face)
                    print(dbg.loop_vertices(face.loop, 2))

                print()

            print("\n".join(dbg.vertex_to_edge_relation()))
            print()


def ijasd():
    a = Path(
        r"C:\Users\chen\Projects\MapsPeople\mi_companion\caddy\tests\fixtures\weird00.dxf"
    )
    doc = ezdxf.readfile(a)
    msp = doc.modelspace()
    doc_out = ezdxf.new()
    msp_out = doc_out.modelspace()

    for b in doc.blocks:
        for q in b.query("3DSOLID"):
            method_name(q, msp_out)

    for e in msp.query("3DSOLID"):
        method_name(e, msp_out)

    doc_out.saveas(a.parent / "meshes.dxf")


ijasd()
