"""
建立測試用的 DXF 檔案
"""
import ezdxf

# 建立新的 DXF 檔案 (AutoCAD 2018 格式)
doc = ezdxf.new('R2018')
msp = doc.modelspace()

# 建立圖層
doc.layers.new('A-WALL-EXT', dxfattribs={'color': 1})  # 紅色 - 外牆
doc.layers.new('A-WALL-INT', dxfattribs={'color': 3})  # 綠色 - 內牆
doc.layers.new('A-WALL-RC', dxfattribs={'color': 5})   # 藍色 - RC牆

# 在 A-WALL-EXT 圖層畫一個矩形 (外牆)
msp.add_line((0, 0), (10000, 0), dxfattribs={'layer': 'A-WALL-EXT'})
msp.add_line((10000, 0), (10000, 8000), dxfattribs={'layer': 'A-WALL-EXT'})
msp.add_line((10000, 8000), (0, 8000), dxfattribs={'layer': 'A-WALL-EXT'})
msp.add_line((0, 8000), (0, 0), dxfattribs={'layer': 'A-WALL-EXT'})

# 在 A-WALL-INT 圖層畫一條內牆
msp.add_line((5000, 0), (5000, 8000), dxfattribs={'layer': 'A-WALL-INT'})

# 在 A-WALL-RC 圖層畫一個 LWPOLYLINE (RC牆)
points = [(2000, 2000), (2000, 6000), (8000, 6000), (8000, 2000), (2000, 2000)]
msp.add_lwpolyline(points, dxfattribs={'layer': 'A-WALL-RC'})

# 儲存檔案
filepath = 'test_sample.dxf'
doc.saveas(filepath)
print(f"[OK] 已建立測試 DXF 檔案: {filepath}")
print(f"     版本: {doc.dxfversion}")
print(f"     圖層數: {len(doc.layers)}")
print(f"     實體數: {len(list(msp))}")
