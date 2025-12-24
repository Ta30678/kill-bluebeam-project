"""
測試資料庫分棟分樓層架構
"""
from database import DatabaseManager
import os

# 清除舊資料庫重新開始
db_file = "test_wall_calculator.db"
if os.path.exists(db_file):
    os.remove(db_file)
    print(f"[OK] 已清除舊資料庫: {db_file}")

# 初始化資料庫
db = DatabaseManager(db_file)

# 建立專案
project_id = db.create_project(
    name="測試專案 - 台善支局",
    source_file="台善支局-建築底圖.dxf",
    notes="分棟分樓層測試"
)
print(f"\n[OK] 已建立專案 ID: {project_id}")

# 建立結構物 (地下層 + 6棟地上層)
print("\n建立結構物...")
basement_id = db.add_building(project_id, "B", "地下層", is_basement=True, display_order=0)
print(f"  [OK] 地下層 ID: {basement_id}")

building_ids = []
for i in range(1, 7):
    building_id = db.add_building(project_id, f"A{i}", f"A{i}棟", is_basement=False, display_order=i)
    building_ids.append(building_id)
    print(f"  [OK] A{i}棟 ID: {building_id}")

# 為地下層建立樓層
print("\n建立地下層樓層...")
db.add_floor(basement_id, "B3F", "地下3樓", floor_level=-3, display_order=0)
db.add_floor(basement_id, "B2F", "地下2樓", floor_level=-2, display_order=1)
db.add_floor(basement_id, "B1F", "地下1樓", floor_level=-1, display_order=2)
print(f"  [OK] 已建立 3 個地下樓層")

# 為 A1 棟建立樓層 (範例)
print("\n建立 A1 棟樓層...")
a1_id = building_ids[0]
floors_a1 = [
    ("1F-6F", "1~6樓", 1, True, 0),
    ("7F-8F", "7~8樓", 7, True, 1),
    ("9F-12F", "9~12樓", 9, True, 2),
    ("13F", "13樓", 13, False, 3),
    ("14F", "14樓", 14, False, 4),
    ("R1F", "R1樓", 15, False, 5),
    ("R2-PRF", "R2~PRF", 16, True, 6),
]

for code, name, level, is_combined, order in floors_a1:
    db.add_floor(a1_id, code, name, floor_level=level, is_combined=is_combined, display_order=order)
    print(f"  [OK] {name}")

# 建立牆類型
print("\n建立牆類型...")
categories = [
    ("EXT", "外牆", "樓高-梁深", "floor_height - beam_depth", "#E74C3C"),
    ("INT", "內牆", "樓高-梁深", "floor_height - beam_depth", "#F1C40F"),
    ("RC", "RC牆", "同樓高", "floor_height", "#1ABC9C"),
]

category_ids = {}
for code, name, height_type, formula, color in categories:
    cat_id = db.add_wall_category(project_id, code, name, height_type, formula, color)
    category_ids[code] = cat_id
    print(f"  [OK] {name} (ID: {cat_id})")

# 查詢測試
print("\n" + "=" * 80)
print("查詢測試")
print("=" * 80)

# 列出所有結構物
buildings = db.get_buildings(project_id)
print(f"\n結構物列表 ({len(buildings)}棟):")
for b in buildings:
    print(f"  - {b['building_code']}: {b['building_name']} (地下層: {b['is_basement']})")

# 列出 A1 棟樓層
floors_a1 = db.get_floors(a1_id)
print(f"\nA1 棟樓層 ({len(floors_a1)}層):")
for f in floors_a1:
    combined = " (合併)" if f['is_combined'] else ""
    print(f"  - {f['floor_code']}: {f['floor_name']}{combined}")

# 列出所有樓層
all_floors = db.get_all_floors_by_project(project_id)
print(f"\n全專案樓層總數: {len(all_floors)}")

print("\n[OK] 資料庫測試完成")
db.close()
