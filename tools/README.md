# 儀表板產生工具

`../index.html` 是最終交付檔(單一自包含 HTML,直接上架即可)。
這個資料夾只是「重新產生」它的工具,平常不需要動。

## 檔案

| 檔案 | 用途 |
|---|---|
| `dashboard_template.html` | 頁面原始碼(含 `__LAND_PATH__` / `__CITY_LIGHTS__` 佔位符),要改版面/文案/測試資料就改這裡 |
| `gen_map.py` | 從 Natural Earth 資料產生大洲形狀路徑 + 城市燈光座標,輸出 `map_land.json` |
| `build_dashboard.py` | 把地圖資料注入模板,輸出 `../index.html` |
| `ne_110m_land.geojson` | Natural Earth 110m 陸地資料(公有領域) |
| `ne_110m_populated_places.geojson` | Natural Earth 110m 世界主要城市(城市燈光的真實位置與人口) |
| `map_land.json` | `gen_map.py` 的輸出(已預先算好) |
| `gen_dots.py`、`map_data.json` | 舊版「點陣風格」地圖產生器,現行版本未使用,保留備用 |

## 重新產生

```
python gen_map.py         # 只有在改投影範圍/簡化程度/燈光大小時才需要
python build_dashboard.py # 重新產出 ../index.html
```

## 常見改動

- **改數據/文案/據點**:直接改 `dashboard_template.html` 裡的 `DASHBOARD_DATA`,再跑 `build_dashboard.py`。
- **接正式 API**:見 `index.html` 檔頭註解——取得同結構資料後呼叫 `renderDashboard(apiData)` 即可。
- **新增據點**:在 `DASHBOARD_DATA.sites` 加一筆(lon/lat 會自動投影),
  `card.x / card.y` 是資訊卡左上角在 1000x470 座標系的位置,挑一塊海面即可。
- **調地圖配色**:模板裡的 `#landGrad`(大洲漸層)、`#lightGrad`(據點光暈)、
  `.land` 的 stroke/drop-shadow。
- **全球城市燈光**:目前只有五個公司據點會發光(亮點=據點)。
  若想加回全球 243 個主要城市的裝飾燈光,把 `build_dashboard.py` 開頭的
  `SHOW_CITY_LIGHTS` 改成 `True` 再重跑即可。
- **活動花絮彈窗**:點擊據點卡片開啟。素材放在各據點的
  `DASHBOARD_DATA.sites[].event`:
  - `activities[]` 一張輪播 = 一個活動(第一個固定放 Launch Party);
    每個活動有 `name`(標題與 📍 活動名)、`src`(照片網址,留空顯示
    佔位圖卡)、`emoji`/`caption`(佔位圖卡用)、`quotes`(該活動的
    同仁留言,跟著輪播切換)
  - **照片規格:16:9,建議 1280x720**(JPG/WebP,每張壓在 300KB 內);
    非 16:9 的照片會被置中裁切(object-fit: cover)。建議由各廠
    Learning Champion 上傳到訓練網站的指定資料夾後填相對路徑
  - `teamsUrl` 填該據點 Teams 頻道連結(demo 值 "#" 不會跳頁),
    留空隱藏按鈕
  - `likes` 是打氣基數;使用者本機 +1 存 localStorage(鍵名
    `llmap-likes`),跨使用者即時總數需另接後端
  - 深連結:`網址#site=據點ID`(如 `#site=WYMY`)直接開啟該據點彈窗,
    適合貼在 Teams 頻道導流
  - 舊資料結構(`title`+`photos`+`quotes`)仍相容:會被視為同一活動
    的多張照片
