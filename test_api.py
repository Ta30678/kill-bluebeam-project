"""
測試 API 上傳和解析 DXF
"""
import requests
import json
import os

API_BASE = "http://localhost:5000/api"

# 測試檔案 - 使用完整的建築底圖
dxf_file = os.path.join("建築底圖test", "白鷺安居-建築底圖_1141121.dxf")  # 138MB - 完整版
# dxf_file = os.path.join("建築底圖test", "白鷺-建築底圖 上構測試用.dxf")  # 95MB
# dxf_file = "test_sample.dxf"  # 小檔案，用於快速測試

print("=" * 80)
print("測試 DXF 上傳與解析")
print("=" * 80)

# 1. 上傳檔案
print("\n步驟 1: 上傳 DXF 檔案...")
with open(dxf_file, 'rb') as f:
    files = {'file': (os.path.basename(dxf_file), f, 'application/octet-stream')}
    response = requests.post(f"{API_BASE}/upload", files=files)

if response.status_code == 200:
    upload_result = response.json()
    print(f"[OK] 上傳成功: {upload_result['filename']}")
    print(f"     儲存路徑: {upload_result['filepath']}")
    filepath = upload_result['filepath']
else:
    print(f"[X] 上傳失敗: {response.text}")
    exit(1)

# 2. 解析 DXF
print("\n步驟 2: 解析 DXF 檔案...")
parse_data = {
    "filepath": filepath,
    "project_name": "白鷺安居測試專案",
    "selected_layers": None  # 不篩選，提取所有圖層
}

response = requests.post(f"{API_BASE}/parse", json=parse_data)

if response.status_code == 200:
    result = response.json()
    print(f"[OK] 解析成功!")
    print(f"     專案 ID: {result['project_id']}")
    print(f"     總線段數: {result['total_segment_count']}")
    print(f"     圖層數: {len(result['layers'])}")

    # 顯示前 20 個圖層
    print(f"\n前 20 個圖層：")
    layers = result['layers']
    for i, (layer_name, layer_info) in enumerate(list(layers.items())[:20]):
        status = layer_info.get('status', 'ON')
        color = layer_info.get('color', '?')
        print(f"  {i+1}. [{status}] {layer_name} (顏色: {color})")

    if len(layers) > 20:
        print(f"  ... 還有 {len(layers) - 20} 個圖層")

    # 顯示線段數量統計
    print(f"\n線段總數: {len(result['segments'])}")
    print(f"前 5 條線段：")
    for i, seg in enumerate(result['segments'][:5]):
        print(f"  {i+1}. 圖層={seg['layer']}, 類型={seg['entity_type']}, 長度={seg['length']:.2f}mm")

    # 按圖層統計
    layer_stats = {}
    for seg in result['segments']:
        layer = seg['layer']
        if layer not in layer_stats:
            layer_stats[layer] = {'count': 0, 'total_length': 0}
        layer_stats[layer]['count'] += 1
        layer_stats[layer]['total_length'] += seg['length']

    print(f"\n按圖層統計（前 10 個）：")
    sorted_layers = sorted(layer_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    for i, (layer, stats) in enumerate(sorted_layers[:10]):
        print(f"  {i+1}. {layer}: {stats['count']} 條線段, 總長 {stats['total_length']/1000:.2f}m")

else:
    print(f"[X] 解析失敗: {response.text}")

print("\n" + "=" * 80)
