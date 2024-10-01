import ezdxf
from ezdxf.addons import Importer
from ezdxf.math import Matrix44
from ezdxf.query import EntityQuery

from caddy.conversion import to_shapely


def per_layer_export(source_doc):
    import tqdm

    source_msp = source_doc.modelspace()
    # create an EntityQuery container with all entities from the modelspace
    source_entities = source_msp.query()
    # get all layer names from entities in the modelspace:
    all_layer_names = [e.dxf.layer for e in source_entities]
    # remove unwanted layers if needed
    for layer_name in tqdm.tqdm(all_layer_names):
        # create a new document for each layer with the same DXF version as the
        # source file
        layer_doc = ezdxf.new(dxfversion=source_doc.dxfversion)
        layer_msp = layer_doc.modelspace()
        importer = Importer(source_doc, layer_doc)
        # select all entities from modelspace from this layer (extended query
        # feature of class EntityQuery)
        entities: EntityQuery = source_entities.layer == layer_name  # type: ignore
        if len(entities):
            importer.import_entities(entities, layer_msp)
            # create required resources
            importer.finalize()
            # layer_doc.saveas(CWD / f"{layer_name}.dxf")

            msp = layer_doc.modelspace()

            # Store geo located DXF entities as GeoJSON data:
            # Get the geo location information from the DXF file:
            geo_data = msp.get_geodata()

            if geo_data:
                # Get transformation matrix and epsg code:
                m, epsg = geo_data.get_crs_transformation()
            else:
                # Identity matrix for DXF files without geo reference data:
                m = Matrix44()

            geoms = []
            for entity in msp.query("*"):
                geoms.append(to_shapely(entity, m))

            from shapely import GeometryCollection

            geom_c = GeometryCollection(geoms)

            with open(f"cool{layer_name}.bro", "w") as f:
                f.write(geom_c.wkt)
