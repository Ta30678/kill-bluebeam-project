"""
測試 DXF 檔案讀取
請將您的 DXF 檔案路徑更新到下方
"""
from dxf_parser import DXFParser

# 請更新為您的 DXF 檔案路徑
dxf_files = [
    r"N:\100_Users\E0056 Wilson\2025-1224 kill bluebeam project\建築底圖\台善支局-建築底圖_1141121.dxf",
    r"N:\100_Users\E0056 Wilson\2025-1224 kill bluebeam project\建築底圖\台善-建築底圖 上情測試用.dxf",
    r"N:\100_Users\E0056 Wilson\2025-1224 kill bluebeam project\建築底圖\台善-建築底圖 下情測試用.dxf",
]

for filepath in dxf_files:
    print("\n" + "=" * 80)
    print(f"測試檔案: {filepath}")
    print("=" * 80)

    parser = DXFParser(filepath)

    if parser.load():
        print("\n[OK] DXF 載入成功！")

        # 提取圖層資訊
        layers = parser.extract_layers()
        print(f"\n找到 {len(layers)} 個圖層")

        # 提取牆線段（不限定圖層前綴，提取所有）
        print("\n開始提取所有線段...")
        segments = parser.extract_wall_entities(wall_layer_prefix=None)

        if segments:
            print(f"\n[OK] 成功提取 {len(segments)} 條線段")

            # 顯示前 5 條線段範例
            print("\n前 5 條線段範例：")
            for seg in segments[:5]:
                print(f"  - {seg.id}: 圖層={seg.layer}, 類型={seg.entity_type}, 長度={seg.length:.2f}mm")

            # 按圖層統計
            parser.print_summary()
        else:
            print("[X] 未找到任何線段")
            print("可能原因：")
            print("  1. 檔案中沒有 LINE、LWPOLYLINE、POLYLINE 實體")
            print("  2. 所有實體都在關閉或凍結的圖層上")

    else:
        print("\n[X] DXF 載入失敗")

    print("\n" + "=" * 80)

print("\n測試完成")
