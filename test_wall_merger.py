"""
Wall Merger Integration Test
測試平行牆合併功能的整合測試
"""

import os
import sys
import sqlite3
import math
from pathlib import Path

# 加入專案路徑
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from database import DatabaseManager
from geometry_utils import (
    LineSegment, are_lines_parallel, perpendicular_distance,
    perpendicular_distance_averaged, calculate_overlap_region,
    find_parallel_pair
)
from wall_merger import WallMerger, pairs_to_dict


def test_geometry_utils():
    """測試幾何計算函式"""
    print("\n" + "=" * 60)
    print("幾何計算函式測試")
    print("=" * 60)

    # 測試水平平行線
    print("\n[測試 1] 水平平行線偵測")
    line1 = LineSegment(start=(0, 0), end=(1000, 0))
    line2 = LineSegment(start=(0, 150), end=(900, 150))

    is_parallel = are_lines_parallel(line1, line2)
    print(f"  平行判斷: {is_parallel}")
    assert is_parallel, "水平線應該被判斷為平行"

    distance = perpendicular_distance_averaged(line1, line2)
    print(f"  垂直距離: {distance:.2f} mm")
    assert abs(distance - 150) < 1, f"距離應該是 150mm，實際是 {distance:.2f}mm"

    overlap = calculate_overlap_region(line1, line2)
    print(f"  重疊長度: {overlap['length']:.2f} mm")
    assert overlap['length'] > 0, "應該有重疊區域"
    print("  [PASS]")

    # 測試垂直平行線
    print("\n[測試 2] 垂直平行線偵測")
    line3 = LineSegment(start=(0, 0), end=(0, 1000))
    line4 = LineSegment(start=(180, 0), end=(180, 800))

    is_parallel = are_lines_parallel(line3, line4)
    print(f"  平行判斷: {is_parallel}")
    assert is_parallel, "垂直線應該被判斷為平行"

    distance = perpendicular_distance_averaged(line3, line4)
    print(f"  垂直距離: {distance:.2f} mm")
    assert abs(distance - 180) < 1, f"距離應該是 180mm，實際是 {distance:.2f}mm"
    print("  [PASS]")

    # 測試斜線 (45 度)
    print("\n[測試 3] 斜線平行偵測 (45度)")
    line5 = LineSegment(start=(0, 0), end=(1000, 1000))
    # 距離 = 150 / sqrt(2) ≈ 106.07 (沿垂直方向)
    # 但我們需要平行線，所以偏移 (150/sqrt(2), 150/sqrt(2))
    offset = 150 / math.sqrt(2)
    line6 = LineSegment(start=(offset, -offset), end=(1000 + offset, 1000 - offset))

    is_parallel = are_lines_parallel(line5, line6)
    print(f"  平行判斷: {is_parallel}")
    assert is_parallel, "45度斜線應該被判斷為平行"
    print("  [PASS]")

    # 測試非平行線
    print("\n[測試 4] 非平行線拒絕")
    line7 = LineSegment(start=(0, 0), end=(1000, 0))
    line8 = LineSegment(start=(0, 0), end=(0, 1000))  # 垂直，不應該被視為平行

    is_parallel = are_lines_parallel(line7, line8)
    print(f"  平行判斷 (應為 False): {is_parallel}")
    assert not is_parallel, "垂直線不應該被判斷為平行"
    print("  [PASS]")

    # 測試 find_parallel_pair
    print("\n[測試 5] find_parallel_pair 整合")
    seg1 = {
        'id': 1, 'segment_uid': 'seg_1', 'dxf_layer': 'WALL-15CM',
        'entity_type': 'LINE', 'start_x': 0, 'start_y': 0,
        'end_x': 10000, 'end_y': 0, 'length': 10000
    }
    seg2 = {
        'id': 2, 'segment_uid': 'seg_2', 'dxf_layer': 'WALL-15CM',
        'entity_type': 'LINE', 'start_x': 0, 'start_y': 150,
        'end_x': 9500, 'end_y': 150, 'length': 9500
    }

    pair = find_parallel_pair(seg1, seg2, wall_thickness=150, tolerance=1.0)
    print(f"  配對結果: {pair is not None}")
    if pair:
        print(f"  主要線段 ID: {pair.primary_id}")
        print(f"  次要線段 ID: {pair.secondary_id}")
        print(f"  距離: {pair.distance:.2f} mm")
        print(f"  重疊長度: {pair.overlap_length:.2f} mm")
        assert pair.primary_id == 1, "較長的線段應該是主要線段"
        assert pair.secondary_id == 2, "較短的線段應該是次要線段"
    assert pair is not None, "應該找到平行對"
    print("  [PASS]")

    print("\n" + "=" * 60)
    print("幾何計算測試全部通過!")
    print("=" * 60)


def test_database_migration():
    """測試資料庫遷移"""
    print("\n" + "=" * 60)
    print("資料庫遷移測試")
    print("=" * 60)

    # 使用測試資料庫
    test_db_path = str(project_dir / 'test_merger.db')

    # 刪除舊的測試資料庫
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = DatabaseManager(test_db_path)

    # 檢查新增的欄位
    cursor = db.conn.cursor()

    # 檢查 wall_categories 表
    cursor.execute("PRAGMA table_info(wall_categories)")
    columns = {row[1]: row for row in cursor.fetchall()}
    print("\n[wall_categories 表欄位]")
    assert 'wall_thickness' in columns, "缺少 wall_thickness 欄位"
    print("  [OK] wall_thickness column exists")
    assert 'wall_thickness_tolerance' in columns, "缺少 wall_thickness_tolerance 欄位"
    print("  [OK] wall_thickness_tolerance column exists")

    # 檢查 wall_segments 表
    cursor.execute("PRAGMA table_info(wall_segments)")
    columns = {row[1]: row for row in cursor.fetchall()}
    print("\n[wall_segments 表欄位]")
    assert 'is_merged' in columns, "缺少 is_merged 欄位"
    print("  [OK] is_merged column exists")
    assert 'merged_into_id' in columns, "缺少 merged_into_id 欄位"
    print("  [OK] merged_into_id column exists")
    assert 'merge_excluded' in columns, "缺少 merge_excluded 欄位"
    print("  [OK] merge_excluded column exists")

    # 檢查 merged_segments 表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='merged_segments'")
    assert cursor.fetchone() is not None, "缺少 merged_segments 表"
    print("\n[merged_segments 表]")
    print("  [OK] merged_segments table exists")

    db.close()

    # 清理測試資料庫
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    print("\n" + "=" * 60)
    print("資料庫遷移測試全部通過!")
    print("=" * 60)


def test_wall_merger_integration():
    """測試 WallMerger 整合功能"""
    print("\n" + "=" * 60)
    print("WallMerger 整合測試")
    print("=" * 60)

    # 使用測試資料庫
    test_db_path = str(project_dir / 'test_merger_integration.db')

    # 刪除舊的測試資料庫
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    db = DatabaseManager(test_db_path)
    merger = WallMerger(db)

    # 建立測試專案
    project_id = db.create_project(name='測試專案', source_file='test.dxf')
    print(f"\n[建立測試專案] ID: {project_id}")

    # 建立牆類型（設定牆厚度）
    category_id = db.add_wall_category(
        project_id=project_id,
        code='W15',
        name='15cm 牆',
        height_type='樓高-梁深',
        height_formula='3200-600',
        color='#E74C3C',
        line_weight=1.5
    )
    print(f"[建立牆類型] ID: {category_id}")

    # 設定牆厚度
    db.update_category(category_id, wall_thickness=150, wall_thickness_tolerance=1.0)
    print("[設定牆厚度] 150mm ±1mm")

    # 匯入測試線段 (使用 import_segments 的格式)
    test_segments = [
        # 平行對 1: 水平線
        {
            'id': 'seg_1', 'layer': 'WALL-15CM', 'entity_type': 'LINE',
            'start_point': [0, 0], 'end_point': [10000, 0], 'length': 10000
        },
        {
            'id': 'seg_2', 'layer': 'WALL-15CM', 'entity_type': 'LINE',
            'start_point': [0, 150], 'end_point': [9500, 150], 'length': 9500
        },
        # 平行對 2: 另一組水平線
        {
            'id': 'seg_3', 'layer': 'WALL-15CM', 'entity_type': 'LINE',
            'start_point': [0, 1000], 'end_point': [5000, 1000], 'length': 5000
        },
        {
            'id': 'seg_4', 'layer': 'WALL-15CM', 'entity_type': 'LINE',
            'start_point': [0, 1150], 'end_point': [6000, 1150], 'length': 6000
        },
        # 單獨線段（不配對）
        {
            'id': 'seg_5', 'layer': 'WALL-15CM', 'entity_type': 'LINE',
            'start_point': [0, 5000], 'end_point': [3000, 5000], 'length': 3000
        },
    ]

    count = db.import_segments(project_id, test_segments)
    print(f"[匯入線段] {count} 條")

    # 設定線段分類
    cursor = db.conn.cursor()
    cursor.execute(
        "UPDATE wall_segments SET category_id = ? WHERE project_id = ?",
        (category_id, project_id)
    )
    db.conn.commit()
    print("[設定分類] 已將所有線段歸類")

    # 偵測平行對
    print("\n[偵測平行對]")
    pairs = merger.find_parallel_pairs(
        project_id=project_id,
        category_id=category_id,
        wall_thickness=150,
        tolerance=1.0
    )
    print(f"  找到 {len(pairs)} 對平行線")

    # 應該找到 2 對
    assert len(pairs) == 2, f"預期找到 2 對，實際找到 {len(pairs)} 對"

    # 檢查第一對
    pair1 = pairs[0]
    print(f"  對 1: 主要={pair1.primary_id}, 次要={pair1.secondary_id}, 距離={pair1.distance:.2f}mm")

    # 轉換為 dict（測試 pairs_to_dict）
    pairs_dict = pairs_to_dict(pairs)
    print(f"  轉換為 dict: {len(pairs_dict)} 項")

    # 套用合併
    print("\n[套用合併]")
    result = merger.apply_merging(project_id, pairs)
    print(f"  套用了 {result.pairs_applied} 對")
    print(f"  合併了 {result.segments_merged} 條線段")
    print(f"  節省長度: {result.total_length_saved:.2f} mm")

    assert result.pairs_applied == 2, "應該套用 2 對"
    assert result.segments_merged == 2, "應該合併 2 條線段"

    # 檢查統計（排除已合併）
    print("\n[統計測試]")
    summary = db.get_summary(project_id, include_merged=False)
    print(f"  有效統計: {len(summary)} 個類型")
    if len(summary) > 0:
        print(f"  類型: {summary[0]['category_name']}")
        print(f"  線段數: {summary[0]['segment_count']}")
        print(f"  總長度: {summary[0]['total_length']:.2f} mm")
        # 應該只有 3 條有效線段 (10000 + 6000 + 3000 = 19000)
        assert summary[0]['segment_count'] == 3, "應該只有 3 條有效線段"

    # 取得合併統計
    stats = merger.get_merge_statistics(project_id)
    print("\n[合併統計]")
    print(f"  總線段數: {stats['total_segments']}")
    print(f"  已合併數: {stats['merged_segments']}")
    print(f"  有效線段數: {stats['effective_segments']}")
    print(f"  合併比例: {stats['merge_ratio']:.2%}")

    # 清除合併
    print("\n[清除合併]")
    cleared = merger.clear_merging(project_id)
    print(f"  清除了 {cleared} 條線段的合併標記")
    assert cleared == 2, "應該清除 2 條"

    # 確認清除成功
    stats2 = merger.get_merge_statistics(project_id)
    assert stats2['merged_segments'] == 0, "清除後不應有已合併線段"
    print("  [PASS] Clear successful")

    db.close()

    # 清理測試資料庫
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

    print("\n" + "=" * 60)
    print("WallMerger 整合測試全部通過!")
    print("=" * 60)


def main():
    """主測試函式"""
    print("\n" + "=" * 60)
    print("平行牆合併系統 - 整合測試")
    print("=" * 60)

    try:
        test_geometry_utils()
        test_database_migration()
        test_wall_merger_integration()

        print("\n" + "=" * 60)
        print("所有測試通過!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1

    except Exception as e:
        print(f"\n測試錯誤: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
