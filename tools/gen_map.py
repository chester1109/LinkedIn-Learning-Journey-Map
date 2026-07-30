# -*- coding: utf-8 -*-
"""Generate solid-continent SVG path + city-light points from Natural Earth data.

Outputs map_land.json:
  land   — projected & simplified SVG path (fill with evenodd)
  lights — [{x, y, r, o}] city glow points sized by population
Same equirectangular projection as gen_dots.py (viewBox 1000x470).
"""
import json, math, os, io

BASE = os.path.dirname(os.path.abspath(__file__))

W, H = 1000.0, 470.0
LON_MIN, LON_MAX = -180.0, 180.0
LAT_MIN, LAT_MAX = -56.0, 78.0
SIMPLIFY_PX = 1.0   # drop successive points closer than this
MIN_RING_PX = 1.6   # drop islands smaller than this bbox

def project(lon, lat):
    x = (lon - LON_MIN) / (LON_MAX - LON_MIN) * W
    y = (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * H
    return x, y

def fmt(v):
    s = ("%.1f" % v).rstrip("0").rstrip(".")
    return s if s else "0"

# ── 陸地路徑 ─────────────────────────────────────────────
with io.open(os.path.join(BASE, "ne_110m_land.geojson"), encoding="utf-8-sig") as f:
    land = json.load(f)

def ring_to_path(ring):
    pts = []
    for lon, lat in ring:
        lat_c = max(LAT_MIN, min(LAT_MAX, lat))  # clamp so Antarctica-adjacent rings close cleanly
        x, y = project(lon, lat_c)
        if pts and abs(x - pts[-1][0]) < SIMPLIFY_PX and abs(y - pts[-1][1]) < SIMPLIFY_PX:
            continue
        pts.append((x, y))
    if len(pts) < 3:
        return ""
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    if max(xs) - min(xs) < MIN_RING_PX and max(ys) - min(ys) < MIN_RING_PX:
        return ""
    # skip rings fully below the lat crop (Antarctica)
    if min(ys) >= H - 0.5:
        return ""
    d = "M" + fmt(pts[0][0]) + " " + fmt(pts[0][1])
    for x, y in pts[1:]:
        d += "L" + fmt(x) + " " + fmt(y)
    return d + "Z"

paths = []
for feat in land["features"]:
    geom = feat["geometry"]
    groups = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    for rings in groups:
        for ring in rings:  # outer + holes; fill-rule evenodd sorts them out
            p = ring_to_path(ring)
            if p:
                paths.append(p)
land_path = "".join(paths)

# ── 城市燈光 ─────────────────────────────────────────────
with io.open(os.path.join(BASE, "ne_110m_populated_places.geojson"), encoding="utf-8-sig") as f:
    places = json.load(f)

lights = []
for feat in places["features"]:
    pr = feat["properties"]
    lon = pr.get("longitude"); lat = pr.get("latitude")
    if lon is None or lat is None:
        lon, lat = feat["geometry"]["coordinates"][:2]
    if not (LAT_MIN < lat < LAT_MAX):
        continue
    x, y = project(lon, lat)
    pop = pr.get("pop_max") or pr.get("pop_min") or 0
    # 光暈半徑 2.2~5.2、亮度 0.35~0.85,依人口對數縮放
    t = 0.0
    if pop > 0:
        t = max(0.0, min(1.0, (math.log10(pop) - 5.0) / 2.5))  # 1e5 → 0, ~3e7 → 1
    r = round(2.2 + t * 3.0, 1)
    o = round(0.35 + t * 0.5, 2)
    lights.append({"x": round(x, 1), "y": round(y, 1), "r": r, "o": o})

out = {"land": land_path, "lights": lights}
with io.open(os.path.join(BASE, "map_land.json"), "w", encoding="utf-8") as f:
    json.dump(out, f)

print("land path chars:", len(land_path), "| rings:", len(paths), "| lights:", len(lights))
