"""
Geometry Utilities for Wall Quantity Calculator
提供平行線偵測、垂直距離計算、重疊區域分析等幾何計算功能
"""
import math
from typing import Tuple, Optional, List
from dataclasses import dataclass


@dataclass
class Vector2D:
    """2D 向量表示"""
    x: float
    y: float

    def length(self) -> float:
        """計算向量長度"""
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self) -> 'Vector2D':
        """正規化向量（單位向量）"""
        l = self.length()
        if l < 1e-10:  # 避免除以零
            return Vector2D(0.0, 0.0)
        return Vector2D(self.x / l, self.y / l)

    def dot(self, other: 'Vector2D') -> float:
        """計算點積"""
        return self.x * other.x + self.y * other.y

    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)

    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)


@dataclass
class LineSegment:
    """線段表示"""
    start: Tuple[float, float]
    end: Tuple[float, float]

    def direction_vector(self) -> Vector2D:
        """取得方向向量"""
        return Vector2D(
            self.end[0] - self.start[0],
            self.end[1] - self.start[1]
        )

    def length(self) -> float:
        """計算線段長度"""
        return self.direction_vector().length()

    def midpoint(self) -> Tuple[float, float]:
        """計算中點"""
        return (
            (self.start[0] + self.end[0]) / 2,
            (self.start[1] + self.end[1]) / 2
        )


def are_lines_parallel(line1: LineSegment, line2: LineSegment,
                       angle_tolerance: float = 1.0) -> bool:
    """
    判斷兩條線段是否平行

    Args:
        line1, line2: 要比較的線段
        angle_tolerance: 角度容許誤差（度），預設 1°

    Returns:
        True 如果兩線平行（在容許誤差內）
    """
    v1 = line1.direction_vector().normalize()
    v2 = line2.direction_vector().normalize()

    # 處理零長度線段
    if v1.length() < 1e-10 or v2.length() < 1e-10:
        return False

    # 使用點積計算夾角的餘弦值
    # cos(θ) = v1 · v2 / (|v1| |v2|)
    # 對於單位向量: cos(θ) = v1 · v2
    dot_product = abs(v1.dot(v2))  # abs 處理反向平行

    # 將容許誤差轉換為弧度
    tolerance_rad = math.radians(angle_tolerance)

    # 平行時 cos(θ) ≈ 1（θ ≈ 0° 或 180°）
    return dot_product >= math.cos(tolerance_rad)


def perpendicular_distance(line1: LineSegment, line2: LineSegment) -> Optional[float]:
    """
    計算兩條平行線之間的垂直距離

    使用點到線距離公式：d = |AB × AP| / |AB|
    其中 AB 是 line1 的方向向量，P 是 line2 的起點

    Args:
        line1: 第一條線段（參考線）
        line2: 第二條線段

    Returns:
        垂直距離，如果計算失敗則返回 None
    """
    # 取 line2 的起點
    p = line2.start

    # line1 定義為 A→B
    a = line1.start
    b = line1.end

    # 計算 2D 叉積: (B-A) × (A-P)
    # 在 2D 中，叉積的 z 分量 = (b.x - a.x) * (a.y - p.y) - (b.y - a.y) * (a.x - p.x)
    bax = b[0] - a[0]
    bay = b[1] - a[1]
    apx = a[0] - p[0]
    apy = a[1] - p[1]

    cross = abs(bax * apy - bay * apx)
    line_length = line1.length()

    if line_length < 1e-10:  # 避免除以零
        return None

    return cross / line_length


def perpendicular_distance_averaged(line1: LineSegment, line2: LineSegment) -> Optional[float]:
    """
    計算兩條平行線之間的平均垂直距離

    取 line2 兩端點到 line1 的距離平均值，更準確處理不完全平行的情況

    Args:
        line1: 第一條線段（參考線）
        line2: 第二條線段

    Returns:
        平均垂直距離
    """
    a = line1.start
    b = line1.end

    # line1 的長度
    line_length = line1.length()
    if line_length < 1e-10:
        return None

    bax = b[0] - a[0]
    bay = b[1] - a[1]

    # 計算 line2 起點到 line1 的距離
    p1 = line2.start
    apx1 = a[0] - p1[0]
    apy1 = a[1] - p1[1]
    cross1 = abs(bax * apy1 - bay * apx1)
    dist1 = cross1 / line_length

    # 計算 line2 終點到 line1 的距離
    p2 = line2.end
    apx2 = a[0] - p2[0]
    apy2 = a[1] - p2[1]
    cross2 = abs(bax * apy2 - bay * apx2)
    dist2 = cross2 / line_length

    return (dist1 + dist2) / 2


def calculate_overlap_region(line1: LineSegment, line2: LineSegment) -> Optional[dict]:
    """
    計算兩條平行線的重疊區域

    將 line2 的端點投影到 line1 的方向向量上，計算重疊區間

    Args:
        line1: 第一條線段（參考線）
        line2: 第二條線段

    Returns:
        dict 包含:
            - 'start': 重疊區域起點座標
            - 'end': 重疊區域終點座標
            - 'length': 重疊長度
            - 't_start': 起點參數值
            - 't_end': 終點參數值
        如果無重疊則返回 None
    """
    # 取得 line1 的方向向量
    v1 = line1.direction_vector()
    v1_len = v1.length()

    if v1_len < 1e-10:
        return None

    # 正規化方向
    v1_norm = Vector2D(v1.x / v1_len, v1.y / v1_len)

    def project_point(point: Tuple[float, float]) -> float:
        """將點投影到 line1 上，返回參數 t"""
        dx = point[0] - line1.start[0]
        dy = point[1] - line1.start[1]
        return dx * v1_norm.x + dy * v1_norm.y

    # 計算所有端點的參數值
    t1_start = 0.0
    t1_end = v1_len
    t2_start = project_point(line2.start)
    t2_end = project_point(line2.end)

    # 確保 t2_start < t2_end
    if t2_start > t2_end:
        t2_start, t2_end = t2_end, t2_start

    # 計算重疊區間
    overlap_start = max(t1_start, t2_start)
    overlap_end = min(t1_end, t2_end)

    if overlap_start >= overlap_end:
        return None  # 無重疊

    # 計算重疊區域的實際座標
    overlap_start_point = (
        line1.start[0] + overlap_start * v1_norm.x,
        line1.start[1] + overlap_start * v1_norm.y
    )
    overlap_end_point = (
        line1.start[0] + overlap_end * v1_norm.x,
        line1.start[1] + overlap_end * v1_norm.y
    )

    return {
        'start': overlap_start_point,
        'end': overlap_end_point,
        'length': overlap_end - overlap_start,
        't_start': overlap_start,
        't_end': overlap_end
    }


def point_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """計算兩點之間的距離"""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    return math.sqrt(dx * dx + dy * dy)


def endpoints_too_close(line1: LineSegment, line2: LineSegment,
                        threshold: float = 50.0) -> bool:
    """
    檢查兩條線的端點是否過於接近（可能是 T 型接頭）

    Args:
        line1, line2: 要檢查的線段
        threshold: 距離閾值（mm）

    Returns:
        True 如果任何端點對之間的距離小於閾值
    """
    endpoints1 = [line1.start, line1.end]
    endpoints2 = [line2.start, line2.end]

    for e1 in endpoints1:
        for e2 in endpoints2:
            if point_distance(e1, e2) < threshold:
                return True
    return False


@dataclass
class ParallelPair:
    """平行線對資訊"""
    primary_id: int        # 主要線段 ID（較長者）
    secondary_id: int      # 次要線段 ID（較短者，將被合併）
    distance: float        # 垂直距離
    overlap_length: float  # 重疊長度
    overlap_region: dict   # 重疊區域詳情


def find_parallel_pair(seg1: dict, seg2: dict,
                       wall_thickness: float,
                       tolerance: float = 1.0,
                       angle_tolerance: float = 1.0,
                       min_overlap: float = 10.0) -> Optional[ParallelPair]:
    """
    檢查兩條線段是否構成平行牆對

    Args:
        seg1, seg2: 線段資料 dict，需包含 id, start_x, start_y, end_x, end_y, length
        wall_thickness: 預期牆厚度 (mm)
        tolerance: 距離容許誤差 (mm)
        angle_tolerance: 角度容許誤差 (度)
        min_overlap: 最小重疊長度 (mm)

    Returns:
        ParallelPair 物件，如果不構成平行對則返回 None
    """
    # 建立 LineSegment 物件
    line1 = LineSegment(
        (seg1['start_x'], seg1['start_y']),
        (seg1['end_x'], seg1['end_y'])
    )
    line2 = LineSegment(
        (seg2['start_x'], seg2['start_y']),
        (seg2['end_x'], seg2['end_y'])
    )

    # 步驟 1: 判斷是否平行
    if not are_lines_parallel(line1, line2, angle_tolerance):
        return None

    # 步驟 2: 計算垂直距離
    dist = perpendicular_distance_averaged(line1, line2)
    if dist is None:
        return None

    # 步驟 3: 檢查距離是否符合牆厚度 ± 容許誤差
    if not (wall_thickness - tolerance <= dist <= wall_thickness + tolerance):
        return None

    # 步驟 4: 計算重疊區域
    overlap = calculate_overlap_region(line1, line2)
    if overlap is None or overlap['length'] < min_overlap:
        return None

    # 步驟 5: 檢查端點是否過近（可能是 T 型接頭）
    # 這個檢查可選，暫時註解掉
    # if endpoints_too_close(line1, line2, threshold=50.0):
    #     return None

    # 步驟 6: 決定主要線段（較長者）與次要線段（較短者）
    len1 = seg1['length']
    len2 = seg2['length']

    if len1 >= len2:
        primary_id = seg1['id']
        secondary_id = seg2['id']
    else:
        primary_id = seg2['id']
        secondary_id = seg1['id']

    return ParallelPair(
        primary_id=primary_id,
        secondary_id=secondary_id,
        distance=dist,
        overlap_length=overlap['length'],
        overlap_region=overlap
    )


# ==================== 測試函式 ====================

def test_geometry():
    """測試幾何計算函式"""
    print("\n" + "=" * 60)
    print("幾何計算函式測試")
    print("=" * 60)

    # 測試 1: 水平平行線
    print("\n測試 1: 水平平行線")
    line1 = LineSegment((0, 0), (1000, 0))
    line2 = LineSegment((0, 150), (1000, 150))

    parallel = are_lines_parallel(line1, line2)
    dist = perpendicular_distance(line1, line2)
    overlap = calculate_overlap_region(line1, line2)

    print(f"  平行: {parallel} (預期: True)")
    print(f"  距離: {dist:.2f} mm (預期: 150.00)")
    print(f"  重疊長度: {overlap['length']:.2f} mm (預期: 1000.00)")

    # 測試 2: 垂直平行線
    print("\n測試 2: 垂直平行線")
    line1 = LineSegment((0, 0), (0, 1000))
    line2 = LineSegment((180, 0), (180, 1000))

    parallel = are_lines_parallel(line1, line2)
    dist = perpendicular_distance(line1, line2)

    print(f"  平行: {parallel} (預期: True)")
    print(f"  距離: {dist:.2f} mm (預期: 180.00)")

    # 測試 3: 45° 斜線平行
    print("\n測試 3: 45° 斜線平行")
    line1 = LineSegment((0, 0), (100, 100))
    line2 = LineSegment((10, 0), (110, 100))  # 偏移 10mm

    parallel = are_lines_parallel(line1, line2)
    dist = perpendicular_distance(line1, line2)
    expected_dist = 10 / math.sqrt(2)  # 約 7.07mm

    print(f"  平行: {parallel} (預期: True)")
    print(f"  距離: {dist:.2f} mm (預期: {expected_dist:.2f})")

    # 測試 4: 非平行線（垂直）
    print("\n測試 4: 非平行線（垂直）")
    line1 = LineSegment((0, 0), (1000, 0))
    line2 = LineSegment((500, 0), (500, 1000))

    parallel = are_lines_parallel(line1, line2)
    print(f"  平行: {parallel} (預期: False)")

    # 測試 5: 部分重疊
    print("\n測試 5: 部分重疊")
    line1 = LineSegment((0, 0), (1000, 0))
    line2 = LineSegment((200, 150), (800, 150))

    overlap = calculate_overlap_region(line1, line2)
    print(f"  重疊長度: {overlap['length']:.2f} mm (預期: 600.00)")
    print(f"  重疊起點: ({overlap['start'][0]:.0f}, {overlap['start'][1]:.0f})")
    print(f"  重疊終點: ({overlap['end'][0]:.0f}, {overlap['end'][1]:.0f})")

    # 測試 6: 無重疊
    print("\n測試 6: 無重疊")
    line1 = LineSegment((0, 0), (100, 0))
    line2 = LineSegment((200, 150), (300, 150))

    overlap = calculate_overlap_region(line1, line2)
    print(f"  重疊: {overlap} (預期: None)")

    # 測試 7: find_parallel_pair 函式
    print("\n測試 7: find_parallel_pair 函式")
    seg1 = {
        'id': 1,
        'start_x': 0, 'start_y': 0,
        'end_x': 10000, 'end_y': 0,
        'length': 10000
    }
    seg2 = {
        'id': 2,
        'start_x': 0, 'start_y': 150,
        'end_x': 9500, 'end_y': 150,
        'length': 9500
    }

    pair = find_parallel_pair(seg1, seg2, wall_thickness=150, tolerance=1.0)
    if pair:
        print(f"  找到平行對!")
        print(f"  主要線段 ID: {pair.primary_id} (預期: 1，因為較長)")
        print(f"  次要線段 ID: {pair.secondary_id} (預期: 2)")
        print(f"  距離: {pair.distance:.2f} mm (預期: 150.00)")
        print(f"  重疊長度: {pair.overlap_length:.2f} mm (預期: 9500.00)")
    else:
        print("  未找到平行對 (錯誤!)")

    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)


if __name__ == "__main__":
    test_geometry()
