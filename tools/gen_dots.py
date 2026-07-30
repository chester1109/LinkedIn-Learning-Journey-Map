# -*- coding: utf-8 -*-
"""Generate dot-matrix world map coordinates from Natural Earth 110m land GeoJSON.

Equirectangular projection, cropped to lat [-56, 78] (drops Antarctica),
lon [-180, 180]. Outputs JSON: dot pixel coords + the 5 site marker coords.
"""
import json, math, os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "ne_110m_land.geojson")
OUT = os.path.join(BASE, "map_data.json")

W, H = 1000.0, 470.0
LON_MIN, LON_MAX = -180.0, 180.0
LAT_MIN, LAT_MAX = -56.0, 78.0
STEP = 7.0  # px grid spacing

def project(lon, lat):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * W
    y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H
    return x, y

def unproject(x, y):
    lon = x / W * (LON_MAX - LON_MIN) + LON_MIN
    lat = LAT_MAX - y / H * (LAT_MAX - LAT_MIN)
    return lon, lat

with open(SRC, "r", encoding="utf-8-sig") as f:
    gj = json.load(f)

# Collect polygons as (bbox, outer_ring, [hole_rings])
polys = []
for feat in gj["features"]:
    geom = feat["geometry"]
    if geom["type"] == "Polygon":
        groups = [geom["coordinates"]]
    elif geom["type"] == "MultiPolygon":
        groups = geom["coordinates"]
    else:
        continue
    for rings in groups:
        outer = rings[0]
        holes = rings[1:]
        xs = [p[0] for p in outer]
        ys = [p[1] for p in outer]
        polys.append(((min(xs), min(ys), max(xs), max(ys)), outer, holes))

def in_ring(lon, lat, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat):
            x_int = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < x_int:
                inside = not inside
        j = i
    return inside

def on_land(lon, lat):
    for (bx0, by0, bx1, by1), outer, holes in polys:
        if lon < bx0 or lon > bx1 or lat < by0 or lat > by1:
            continue
        if in_ring(lon, lat, outer):
            for h in holes:
                if in_ring(lon, lat, h):
                    break
            else:
                return True
    return False

dots = []
ny = int(H / STEP)
nx = int(W / STEP)
for iy in range(ny + 1):
    y = iy * STEP + STEP / 2
    # slight horizontal offset on alternating rows for organic texture
    x_off = (STEP / 2) if iy % 2 == 0 else STEP
    for ix in range(nx + 1):
        x = ix * STEP + x_off
        if x > W:
            continue
        lon, lat = unproject(x, y)
        if on_land(lon, lat):
            dots.append((round(x), round(y)))

SITES = {
    "WYHQ":    (121.663, 25.065),   # 新北市汐止區
    "WYTN":    (120.237, 23.121),   # 台南市安定區
    "WYMY":    (103.663, 1.641),    # Senai, Johor, Malaysia
    "Seattle": (-122.137, 47.627),  # Bellevue, WA
    "WYMX":    (-106.424, 31.652),  # Cd. Juárez, Chihuahua
}
markers = {}
for name, (lon, lat) in SITES.items():
    x, y = project(lon, lat)
    markers[name] = {"x": round(x, 1), "y": round(y, 1), "land": on_land(lon, lat)}

with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"w": W, "h": H, "dots": dots, "markers": markers}, f)

print("dots:", len(dots))
print("markers:", json.dumps(markers, indent=1))
