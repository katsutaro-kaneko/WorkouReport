#
#        プログラム名：MapGraph.py
#
#        使用方法：
#            1, 変換するファイルを、本コードと同じディレクトリーに移動をする
#            2, コンソールを立ち上げ、本コードのあるディレクトリーへ移動する．
#            3, コマンドラインの入力: python3 MapGraph.py "変換ファイル名.拡張子"
#               注意： Macのfinderで表示されているファイル名とコンソールのlsコマンド表示される
#                       名称が違っている場合があります． "/"と":"が変わる場合があるので注意してください．
#            4,  同じディレクトリー内に、map.htmlとspeed_altitude.pngというファイルができる．
#       ．
#         使用上の注意：
#            importするライブラリを事前にインストールしておく必要があります．
#                   pip install matplotlib
#                   pip install folium
#

import sys
import json
import math
import matplotlib.pyplot as plt
import folium

#   ---  変換するファイル名を貼り付ける
fname = sys.argv[1]

#
#   -----------   経路を表示させるための def  ----------------
#

# --- 地球上の2点間距離（Haversine） ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371e3  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c  # meters

#
#   -----------   速度と高度を表示させるための def  ----------------
#

def load_tracks(path):
    """JSONファイルから軌跡データを読み込み、グループごとに座標リストを返す"""
    with open(path, "r") as f:
        data = json.load(f)

    groups = data["totalRecord"]["groups"]

    tracks = []  # 各グループの [ (lat, lon), ... ] を入れる

    for g in groups:
        points = []
        for loc in g["locationData"]:
            lat = loc.get("latitude")
            lon = loc.get("longitude")
            if lat is not None and lon is not None:
                points.append((lat, lon))
        tracks.append({
            "groupNo": g["groupNo"],
            "startTime": g["startTime"],
            "endTime": g["endTime"],
            "points": points
        })

    return tracks

#
#   -----------   プログラムの開始  ----------------
#
#        ------------   経路データの作成  ----------
#

#    -- 読み込むファイル名を下の行に貼り付ける -- 
# fname = "report_2025-11-15T00:31:24Z.json"

tracks = load_tracks(fname)

print("ファイルを開きました．")

# 最初のポイントに地図を合わせる
first_lat, first_lon = tracks[0]["points"][0]

m = folium.Map(location=[first_lat, first_lon], zoom_start=14)

for tr in tracks:
    folium.PolyLine(
        locations=tr["points"],
        popup=f"Group {tr['groupNo']}",
        weight=4,
        opacity=0.8
    ).add_to(m)

m.save("map.html")
print("map.html に出力しました")

#
#        ------------   速度、高度グラフの作成  ----------
#
#
# --- JSON 読み込み ---
with open(fname, "r") as f:
    data = json.load(f)

# --- データ取り出し ---
distances = [0.0]  # 距離（累積）
speeds_kmh = []    # 速度（km/h）
altitudes = []     # 高度（m）

last_lat = None
last_lon = None

for group in data["totalRecord"]["groups"]:
    for loc in group["locationData"]:

        lat = loc.get("latitude")
        lon = loc.get("longitude")
        speed = loc.get("speed")
        alt = loc.get("altitude")

        if lat is None or lon is None or speed is None:
            continue

        # 距離計算
        if last_lat is not None:
            d = haversine(last_lat, last_lon, lat, lon)
            distances.append(distances[-1] + d)
        else:
            distances = [0.0]

        # 速度を km/h に変換 (m/s × 3.6)
        speeds_kmh.append(speed * 3.6)
        altitudes.append(alt)

        last_lat = lat
        last_lon = lon

# --- 距離を km に変換 ---
dist_km = [d / 1000.0 for d in distances[:len(speeds_kmh)]]

# --- グラフ作成 ---
fig, ax1 = plt.subplots(figsize=(10, 5))

# ---- 速度プロット（左軸） ----
ax1.plot(dist_km, speeds_kmh, label="Speed (km/h)", color="tab:blue")
ax1.set_xlabel("Distance (km)")
ax1.set_ylabel("Speed (km/h)", color="tab:blue")
ax1.tick_params(axis='y', labelcolor="tab:blue")

# ---- 高度プロット（右軸） ----
ax2 = ax1.twinx()
ax2.plot(dist_km, altitudes, label="Altitude (m)", color="tab:red")
ax2.set_ylabel("Altitude (m)", color="tab:red")
ax2.tick_params(axis='y', labelcolor="tab:red")

# ---- タイトルとグリッド ----
plt.title("Speed & Altitude vs Distance")
ax1.grid(True)

plt.tight_layout()
#   plt.show()

plt.savefig("speed_altitude.png")

print("グラフの作成を終了しました．")
f.close()
print("ファイルをCloseしました")

'''
Copyright (c) 2025 Katsutaro Kaneko

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''
