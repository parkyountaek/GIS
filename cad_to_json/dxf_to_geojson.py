#-*- coding:utf-8 -*-
"""
타입
* Face3d
* Solid3d
* Arc - 처리완료
* Attrib
* Body
* Circle - 처리완료
* Dimension
* ArcDimension
* Ellipse
* Hatch
* Image
* Insert - 나머지 것들 처리되면 다 완료됨
* Leader - 처리완료
* Line - 처리완료
* LWPolyline - 처리완료
* MLine
* Mesh
* MPolygon
* MText - 처리완료
* Point - 처리완료
* Polyline - 처리완료
* Vertex
* Polymesh
* Polyface
* Ray
* Region
* Shape
* Solid - 처리완료
* Spline - 처리완료
* Surface
* Text - 처리완료
* Trace
* Underlay
* Viewport
* Wipeout
* XLine

https://ezdxf.readthedocs.io/en/stable/reference.html#dxf-structures


author: park youn taek
version: 1.0
description: dxf to geojson save code
             "not_insert_converter" function need to update following each type
             !encoding is important!

"""

import ezdxf
import copy
from ezdxf.tools.rgb import DXF_DEFAULT_COLORS, int2rgb
import json
import re
regex = re.compile(r'\([^)]*\)')

defaultType = {
  "FeatureCollection": {
    "type": "FeatureCollection",
    "features": []
  },
  "Point": {
    "type": "Feature",
    "geometry": {
      "type": "Point",
      "coordinates": []
    },
    "properties": {
        
    }
  },
  "LineString": {
    "type": "Feature",
    "geometry": {
      "type": "LineString",
      "coordinates": [
        []
      ]
    },
    "properties": {
        
    }
  },
  "Polygon": {
    "type": "Feature",
    "geometry": {
      "type": "Polygon",
      "coordinates": [
        [
          []
        ]
      ]
    },
    "properties": {
        
    }
  }
}

result = []
def findColor(m):
  rgb24 = DXF_DEFAULT_COLORS[m.dxf.color-1]
  return '#%02x%02x%02x' % int2rgb(rgb24)

def findColor1(m):
  find = regex.findall(str(m))
  if len(find) != 0:
    color = find[0][1:-1]
    if len(color) < 7:
      color=color+str(0)*(7-len(color))
    return color
  return None

def not_insert_converter(m, baseLoc, insert):
  if m.dxftype() == 'POINT':
    point = copy.deepcopy(defaultType["Point"])
    point["properties"]["color"] = findColor1(m)
    point["geometry"]["coordinates"] = [baseLoc[0]+m.dxf.location[0], baseLoc[1]+m.dxf.location[1]]
    point["properties"]["actype"] = "INSERT-"+str(m.dxftype()) if insert else str(m.dxftype())
    result.append(point)
  elif m.dxftype() in ['TEXT', 'MTEXT']:
    text = copy.deepcopy(defaultType["Point"])
    text["properties"]["actype"] = "INSERT-"+str(m.dxftype()) if insert else str(m.dxftype())
    text["properties"]["color"] = findColor1(m)
    text["properties"]["sort"] = m.get_pos()[0] if m.dxftype() == 'TEXT' else 'CENTER'
    text["properties"]["text"] = str(m.dxf.text).encode().decode('utf8')
    if insert:
      text["properties"]["origin"] = baseLoc
    text["properties"]["rotation"] = m.dxf.rotation
    text["properties"]["textHeight"] = m.dxf.height if m.dxftype() == 'TEXT' else 10
    text["geometry"]["coordinates"] = [baseLoc[0]+m.get_pos()[1][0], baseLoc[1]+m.get_pos()[1][1]] if m.dxftype() == 'TEXT' else [baseLoc[0]+m.dxf.insert[0], baseLoc[1]+m.dxf.insert[1]]
    result.append(text)
    texts.append(text)
  elif m.dxftype() in ['LINE', 'POLYLINE', 'LWPOLYLINE']:
    line = copy.deepcopy(defaultType["LineString"])
    line["properties"]["color"] = findColor1(m)
    line["properties"]["thickness"] = m.dxf.thickness
    line["properties"]["actype"]="INSERT-"+str(m.dxftype()) if insert else str(m.dxftype())
    if insert:
      line["properties"]["origin"] = baseLoc
      line["properties"]["xscale"]=insert.dxf.xscale
      line["properties"]["yscale"]=insert.dxf.yscale
      line["properties"]["rotation"]=insert.dxf.rotation
      line["properties"]["name"]=insert.dxf.name
    if m.dxftype() == 'LINE':
        line["geometry"]["coordinates"]=[[baseLoc[0]+m.dxf.start[0], baseLoc[1]+m.dxf.start[1]], [baseLoc[0]+m.dxf.end[0], baseLoc[1]+m.dxf.end[1]]]
    elif m.dxftype() in ['LWPOLYLINE', 'POLYLINE']:
      location = []
      for v in m.vertices:
        location.append([baseLoc[0]+v.dxf.location[0], baseLoc[1]+v.dxf.location[1]])
      if m.dxf.flags != 0:
        location.append(location[0])
      line["geometry"]["coordinates"] = location
    result.append(line)
  elif m.dxftype() == 'CIRCLE':
    circle = copy.deepcopy(defaultType["Point"])
    circle["properties"]["actype"] = "INSERT-"+str(m.dxftype()) if insert else str(m.dxftype())
    circle["properties"]["color"] = findColor1(m)
    circle["geometry"]["coordinates"] = [baseLoc[0]+m.dxf.center[0], baseLoc[1]+m.dxf.center[1]]
    circle["properties"]["radius"]= m.dxf.radius
    result.append(circle)
  elif m.dxftype() == 'SOLID':
    polygon = copy.deepcopy(defaultType["Polygon"])
    polygon["properties"]["color"] = findColor1(m)
    polygon["properties"]["actype"] = "INSERT-"+str(m.dxftype()) if insert else str(m.dxftype())
    if insert:
      polygon["properties"]["origin"] = baseLoc
      polygon["properties"]["xscale"]=insert.dxf.xscale
      polygon["properties"]["yscale"]=insert.dxf.yscale
      polygon["properties"]["rotation"]=insert.dxf.rotation
    location = []
    for vertex in m.vertices():
      location.append([baseLoc[0]+vertex[0], baseLoc[1]+vertex[1]])
    polygon["geometry"]["coordinates"] = [location]
    result.append(polygon)
  elif m.dxftype() in ['ARC', 'SPLINE'] :
    if m.dxftype() == 'ARC':
      spline = m.to_spline()
    else:
      spline = m
    location = []
    vertics = spline.control_points
    for vertex in vertics:
      location.append([baseLoc[0]+vertex[0], baseLoc[1]+vertex[1]])
    if spline.closed:
      location.append([baseLoc[0]+vertics[0][0], baseLoc[1]+vertics[0][1]])
    line = copy.deepcopy(defaultType["LineString"])
    if insert:
      line["properties"]["origin"] = baseLoc
      line["properties"]["xscale"]=insert.dxf.xscale
      line["properties"]["yscale"]=insert.dxf.yscale
      line["properties"]["rotation"]=insert.dxf.rotation
    line["properties"]["color"] = findColor1(spline)
    line["properties"]["actype"] = "INSERT-"+str(m.dxftype()) if insert else str(m.dxftype())
    line["geometry"]["coordinates"] = location
    result.append(line)


def insert_converter(m):
  baseLoc = [m.dxf.insert[0], m.dxf.insert[1]]
  for block in m.block():
    not_insert_converter(block, baseLoc, m)        

if __name__ == '__main__':      
  try:
    encoding='cp949'
    filename = "filename.dxf"
    dxf = ezdxf.readfile(filename, encoding=encoding)
    print("version : ", dxf.dxfversion)

    # msp = dxf.modelspace()
    # for m in msp:
    #   if m.dxftype() != 'INSERT':
    #     not_insert_converter(m, [0, 0], None)
    #   else:
    #     insert_converter(m)


    for x in dxf.entities.__iter__():
      if 'VIEWPORT' not in str(x):
        not_insert_converter(x, [0, 0], None)

    with open(filename.replace('.dxf', '-converted.json'), 'w', encoding='utf-8-sig') as json_file:
      json_file.write(json.dumps(result, indent=4, ensure_ascii=False))
    print("SUCCESS")
  except Exception as e:
    print("EXCEPTION :", e)