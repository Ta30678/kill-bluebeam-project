"""
測試本地 DXF 檔案讀取
"""
from dxf_parser import DXFParser

filepath = "test_sample.dxf"

print("=" * 80)
print(f"測試檔案: {filepath}")
print("=" * 80)

parser = DXFParser(filepath)

if parser.load():
    print("\n[OK] DXF 載入成功！")

    # 提取圖層資訊
    layers = parser.extract_layers()
    print(f"\n找到 {len(layers)} 個圖層")

    # 提取牆線段（A-WALL 開頭）
    print("\n開始提取 A-WALL 開頭的線段...")
    segments = parser.extract_wall_entities(wall_layer_prefix="A-WALL")

    if segments:
        print(f"\n[OK] 成功提取 {len(segments)} 條線段")

        # 顯示所有線段
        print("\n線段詳情：")
        for seg in segments:
            print(f"  - {seg.id}: 圖層={seg.layer}, 類型={seg.entity_type}, 長度={seg.length:.2f}mm")

        # 按圖層統計
        parser.print_summary()
    else:
        print("[X] 未找到任何線段")

else:
    print("\n[X] DXF 載入失敗")

print("\n" + "=" * 80)
