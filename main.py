import ezdxf
from ezdxf.addons import geo
from shapely.geometry import shape


def retransform_pyproj():
  from pyproj import Transformer
  from ezdxf.math import Vec3

  # GPS track in WGS84, load_gpx_track() code see above
  gpx_points = list(load_gpx_track('track1.gpx'))

  # Create transformation object:
  ct = Transformer.from_crs('EPSG:4326', 'EPSG:3395')

  # Create GeoProxy() object:
  geo_proxy = GeoProxy.parse({
    'type': 'LineString',
    'coordinates': gpx_points
  })

  # Apply a custom transformation function to all coordinates:
  geo_proxy.apply(lambda v: Vec3(ct.transform(v.x, v.y)))


def to_shapely():
  # Load DXF document including HATCH entities.
  doc = ezdxf.readfile('hatch.dxf')
  msp = doc.modelspace()

  # Test a single entity
  # Get the first DXF hatch entity:
  hatch_entity = msp.query('HATCH').first

  # Create GeoProxy() object:
  hatch_proxy = geo.proxy(hatch_entity)

  # Shapely supports the __geo_interface__
  shapely_polygon = shape(hatch_proxy)

  if shapely_polygon.is_valid:
    ...
  else:
    print(f'Invalid Polygon from {str(hatch_entity)}.')

  # Remove invalid entities by a filter function
  def validate(geo_proxy: geo.GeoProxy) -> bool:
    # Multi-entities are divided into single entities:
    # e.g. MultiPolygon is verified as multiple single Polygon entities.
    if geo_proxy.geotype == 'Polygon':
      return shape(geo_proxy).is_valid
    return True

  # The gfilter() function let only pass compatible DXF entities
  msp_proxy = geo.GeoProxy.from_dxf_entities(geo.gfilter(msp))

  # remove all mappings for which validate() returns False
  msp_proxy.filter(validate)


def transform_osr():
  from osgeo import osr
  from ezdxf.math import Vec3

  # GPS track in WGS84, load_gpx_track() code see above
  gpx_points = list(load_gpx_track('track1.gpx'))

  # Create source coordinate system:
  src_datum = osr.SpatialReference()
  src_datum.SetWellKnownGeoCS('WGS84')

  # Create target coordinate system:
  target_datum = osr.SpatialReference()
  target_datum.SetWellKnownGeoCS('EPSG:3395')

  # Create transformation object:
  ct = osr.CoordinateTransform(src_datum, target_datum)

  # Create GeoProxy() object:
  geo_proxy = GeoProxy.parse({
    'type': 'LineString',
    'coordinates': gpx_points
  })

  # Apply a custom transformation function to all coordinates:
  geo_proxy.apply(lambda v: Vec3(ct.TransformPoint(v.x, v.y)))


def to_ogr():
  from osgeo import ogr
  from ezdxf.addons import geo
  from ezdxf.render import random_2d_path
  import json

  p = geo.GeoProxy({'type': 'LineString', 'coordinates': list(random_2d_path(20))})
  # Create a GeoJSON string from the __geo_interface__ object by the json
  # module and feed the result into ogr:
  line_string = ogr.CreateGeometryFromJson(json.dumps(p.__geo_interface__))

  # Parse the GeoJSON string from ogr by the json module and feed the result
  # into a GeoProxy() object:
  p2 = geo.GeoProxy.parse(json.loads(line_string.ExportToJson()))
