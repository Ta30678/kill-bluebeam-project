"""
測試實際 DXF 檔案讀取
"""
from dxf_parser import DXFParser
import os

# 測試建築底圖test目錄中的檔案
test_dir = "建築底圖test"
dxf_file = os.path.join(test_dir, "白鷺-建築底圖 上構測試用.dxf")

print("=" * 80)
print(f"測試檔案: {dxf_file}")
print("=" * 80)

parser = DXFParser(dxf_file)

if parser.load():
    print("\n[OK] DXF 載入成功！")

    # 提取圖層資訊
    layers = parser.extract_layers()
    print(f"\n找到 {len(layers)} 個圖層：")
    for layer_name, layer_info in list(layers.items())[:20]:  # 只顯示前20個
        print(f"  [{layer_info['status']}] {layer_name} (顏色: {layer_info['color']})")

    if len(layers) > 20:
        print(f"  ... 還有 {len(layers) - 20} 個圖層")

    # 提取所有線段（不限定圖層前綴）
    print("\n開始提取所有線段...")
    segments = parser.extract_wall_entities(wall_layer_prefix=None)

    if segments:
        print(f"\n[OK] 成功提取 {len(segments)} 條線段")

        # 顯示前 10 條線段範例
        print("\n前 10 條線段範例：")
        for seg in segments[:10]:
            print(f"  - {seg.id}: 圖層={seg.layer}, 類型={seg.entity_type}, 長度={seg.length:.2f}mm")

        # 按圖層統計
        parser.print_summary()
    else:
        print("[X] 未找到任何線段")
else:
    print("\n[X] DXF 載入失敗")

print("\n" + "=" * 80)
