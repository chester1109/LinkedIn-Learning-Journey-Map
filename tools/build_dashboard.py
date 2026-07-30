# -*- coding: utf-8 -*-
"""Inject precomputed continent path + city lights into the dashboard template."""
import json, os, io

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.dirname(BASE)  # tools/ 的上一層,即 index.html 所在資料夾
OUT = os.path.join(OUT_DIR, "index.html")

# 城市燈光開關:False = 地圖上只有五個公司據點會發光(亮點代表據點);
# True = 額外顯示全球 243 個主要城市的燈光(純裝飾)
SHOW_CITY_LIGHTS = False

with io.open(os.path.join(BASE, "map_land.json"), encoding="utf-8") as f:
    data = json.load(f)

def fmt(v):
    s = ("%.1f" % v).rstrip("0").rstrip(".")
    return s if s else "0"

# 每個城市 = 外圈光暈(radialGradient)+ 內核亮點
parts = []
for l in data["lights"] if SHOW_CITY_LIGHTS else []:
    halo_r = l["r"] * 2.6
    core_r = 0.8 + (l["r"] - 2.2) * 0.35
    core_o = min(0.95, l["o"] + 0.15)
    parts.append(
        '<circle cx="%s" cy="%s" r="%s" fill="url(#lightGrad)" opacity="%s"/>'
        % (fmt(l["x"]), fmt(l["y"]), fmt(halo_r), l["o"])
    )
    parts.append(
        '<circle cx="%s" cy="%s" r="%s" fill="#ffe3a6" opacity="%s"/>'
        % (fmt(l["x"]), fmt(l["y"]), fmt(core_r), core_o)
    )
lights_svg = "".join(parts)

with io.open(os.path.join(BASE, "dashboard_template.html"), encoding="utf-8") as f:
    html = f.read()

assert "__LAND_PATH__" in html and "__CITY_LIGHTS__" in html
html = html.replace("__LAND_PATH__", data["land"]).replace("__CITY_LIGHTS__", lights_svg)

with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(html)

print("written:", OUT, "size:", os.path.getsize(OUT), "bytes | lights:", len(data["lights"]))
