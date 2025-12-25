"""
DXF Parser for Wall Quantity Calculator
提取 DXF 檔案中的圖層資訊和幾何實體，計算各類型牆的長度
使用 DXF Group Codes 資料庫進行解析
"""
import ezdxf
import math
import json
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict, field

# 導入 DXF 組碼資料庫
try:
    from dxf_group_codes import (
        DXF_GROUP_CODES, DXF_HEADER_VARIABLES, DXF_ENTITY_TYPES,
        get_group_code_info, get_header_variable_info, get_entity_type_info,
        get_units_conversion_factor, interpret_group_code, GroupCodeCategory
    )
    DXF_DB_AVAILABLE = True
except ImportError:
    DXF_DB_AVAILABLE = False
    print("[!] DXF Group Codes database not available")

@dataclass
class WallSegment:
    """代表一條牆線段"""
    id: str
    layer: str
    entity_type: str
    start_point: Tuple[float, float]
    end_point: Tuple[float, float]
    length: float
    vertices: List[Tuple[float, float]] = None  # For polylines
    
    def to_dict(self):
        return asdict(self)

class DXFParser:
    """解析 DXF 檔案並提取牆線段資訊"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.doc = None
        self.layers: Dict[str, dict] = {}
        self.segments: List[WallSegment] = []
        self._segment_counter = 0
        self.dimscale = 1.0  # DXF DIMSCALE 變數（尺寸縮放比例）
        self.insunits = 0    # DXF INSUNITS 變數（插入單位）
    
    def load(self):
        """載入 DXF 檔案（支援多種版本和編碼）"""
        import os

        # 檢查檔案是否存在
        if not os.path.exists(self.filepath):
            print(f"[X] 檔案不存在: {self.filepath}")
            return False

        # 嘗試多種方式讀取
        attempts = [
            ("預設讀取", lambda: ezdxf.readfile(self.filepath)),
            ("指定 UTF-8 編碼", lambda: ezdxf.readfile(self.filepath, encoding='utf-8')),
            ("指定 CP950 編碼 (繁中)", lambda: ezdxf.readfile(self.filepath, encoding='cp950')),
            ("指定 GBK 編碼 (簡中)", lambda: ezdxf.readfile(self.filepath, encoding='gbk')),
            ("自動修復模式", lambda: ezdxf.recover.readfile(self.filepath)),
        ]

        for method_name, read_func in attempts:
            try:
                print(f">> 嘗試 {method_name}...")
                self.doc = read_func()
                print(f"[OK] 成功載入 DXF 檔案: {self.filepath}")
                print(f"     DXF 版本: {self.doc.dxfversion}")
                print(f"     使用方法: {method_name}")

                # 檢查檔案是否有效
                if self.doc.modelspace() is None:
                    print("     [!] 警告：模型空間為空")
                    continue

                # 讀取 DXF 標頭變數
                try:
                    self.dimscale = self.doc.header.get('$DIMSCALE', 1.0)
                    print(f"     DIMSCALE: {self.dimscale}")
                except:
                    self.dimscale = 1.0
                    print("     DIMSCALE: 1.0 (預設)")

                try:
                    self.insunits = self.doc.header.get('$INSUNITS', 0)
                    units_map = {
                        0: "未指定", 1: "英寸", 2: "英尺", 3: "英里",
                        4: "毫米", 5: "公分", 6: "公尺", 7: "公里"
                    }
                    print(f"     INSUNITS: {self.insunits} ({units_map.get(self.insunits, '其他')})")
                except:
                    self.insunits = 0
                    print("     INSUNITS: 0 (未指定)")

                return True

            except IOError as e:
                if method_name == attempts[-1][0]:  # 最後一次嘗試
                    print(f"[X] 無法讀取檔案: {e}")
                continue

            except ezdxf.DXFStructureError as e:
                if method_name == attempts[-1][0]:
                    print(f"[X] DXF 檔案結構錯誤: {e}")
                continue

            except UnicodeDecodeError as e:
                if method_name == attempts[-1][0]:
                    print(f"[X] 編碼錯誤: {e}")
                continue

            except Exception as e:
                if method_name == attempts[-1][0]:
                    print(f"[X] 未知錯誤: {type(e).__name__}: {e}")
                continue

        print("\n[X] 所有讀取方法都失敗")
        print("建議：")
        print("  1. 確認檔案不是 DWG 格式（需先轉換為 DXF）")
        print("  2. 使用 ODA File Converter 重新轉換，選擇較舊的 DXF 版本（如 2018 ASCII DXF）")
        print("  3. 在 AutoCAD 中開啟後另存為 DXF，選擇 'AutoCAD 2018 DXF' 格式")
        return False
    
    def extract_layers(self) -> Dict[str, dict]:
        """提取所有圖層資訊"""
        if not self.doc:
            return {}
        
        for layer in self.doc.layers:
            self.layers[layer.dxf.name] = {
                "name": layer.dxf.name,
                "color": layer.dxf.color,
                "is_on": layer.is_on(),
                "is_frozen": layer.is_frozen(),
                "status": "ON" if layer.is_on() and not layer.is_frozen() else "OFF"
            }

        # 避免 Unicode 編碼錯誤，不直接 print
        print(f"\n找到 {len(self.layers)} 個圖層")

        return self.layers
    
    def extract_header_info(self) -> Dict[str, Any]:
        """
        提取並解釋 DXF 標頭變數
        使用 DXF Group Codes 資料庫進行解釋
        """
        if not self.doc:
            return {}
        
        header_info = {}
        
        # 常用的標頭變數列表
        important_vars = [
            '$DIMSCALE', '$DIMLFAC', '$INSUNITS', '$LUNITS', '$LUPREC',
            '$EXTMIN', '$EXTMAX', '$LIMMIN', '$LIMMAX',
            '$CLAYER', '$CECOLOR', '$CELTYPE', '$LTSCALE',
            '$ACADVER', '$DWGCODEPAGE'
        ]
        
        for var_name in important_vars:
            try:
                value = self.doc.header.get(var_name)
                if value is not None:
                    var_info = {
                        "value": value,
                        "raw_value": str(value)
                    }
                    
                    # 使用 DXF 組碼資料庫提供詳細資訊
                    if DXF_DB_AVAILABLE:
                        db_info = get_header_variable_info(var_name)
                        if db_info:
                            var_info["description_zh"] = db_info.get("description_zh", "")
                            var_info["description_en"] = db_info.get("description_en", "")
                            var_info["type"] = db_info.get("type", "unknown")
                            
                            # 如果有值對照表，提供解釋
                            if "values" in db_info and value in db_info["values"]:
                                var_info["interpreted"] = db_info["values"][value]
                    
                    header_info[var_name] = var_info
            except Exception as e:
                print(f"  [!] 無法讀取 {var_name}: {e}")
        
        # 輸出重要資訊摘要
        print(f"\n=== DXF 標頭變數摘要 ===")
        print(f"  DIMSCALE: {header_info.get('$DIMSCALE', {}).get('value', 'N/A')}")
        print(f"  INSUNITS: {header_info.get('$INSUNITS', {}).get('value', 'N/A')}")
        if DXF_DB_AVAILABLE and '$INSUNITS' in header_info:
            insunits = header_info['$INSUNITS'].get('value', 0)
            units_info = get_header_variable_info('$INSUNITS')
            if units_info and 'values' in units_info:
                print(f"           ({units_info['values'].get(insunits, '未知')})")
        
        return header_info
    
    def get_calculated_scale(self) -> float:
        """
        計算真實的比例係數
        結合 DIMSCALE 和 INSUNITS 計算正確的測量比例
        """
        # 基本比例 = DIMSCALE
        scale = self.dimscale
        
        # 如果有 INSUNITS，可以進一步調整
        if DXF_DB_AVAILABLE and self.insunits > 0:
            # 取得單位轉換係數（轉為毫米）
            unit_factor = get_units_conversion_factor(self.insunits, "mm")
            # 如果單位不是毫米，需要調整
            if unit_factor != 1.0:
                print(f"  單位轉換係數: {unit_factor}")
        
        return scale
    
    def _generate_id(self) -> str:
        """生成唯一 ID"""
        self._segment_counter += 1
        return f"seg_{self._segment_counter:05d}"
    
    def _calculate_length(self, start: Tuple, end: Tuple) -> float:
        """計算兩點間距離"""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _calculate_polyline_length(self, vertices: List[Tuple]) -> float:
        """計算多段線總長度"""
        total = 0.0
        for i in range(len(vertices) - 1):
            total += self._calculate_length(vertices[i], vertices[i + 1])
        return total
    
    def _transform_point(self, point: Tuple[float, float], 
                         insert: Tuple[float, float], 
                         rotation: float, 
                         x_scale: float, 
                         y_scale: float) -> Tuple[float, float]:
        """
        將圖塊內的座標轉換到世界座標
        處理縮放、旋轉和平移變換
        """
        x, y = point
        # 先縮放
        x *= x_scale
        y *= y_scale
        # 再旋轉
        cos_r = math.cos(rotation)
        sin_r = math.sin(rotation)
        rx = x * cos_r - y * sin_r
        ry = x * sin_r + y * cos_r
        # 最後平移
        return (rx + insert[0], ry + insert[1])
    
    def extract_wall_entities(self, wall_layer_prefix: str = "A-WALL") -> List[WallSegment]:
        """
        提取牆相關的實體
        預設只提取以 'A-WALL' 開頭的圖層（建築圖層命名慣例）
        """
        if not self.doc:
            return []
        
        msp = self.doc.modelspace()
        
        # 處理 LINE 實體
        for entity in msp.query("LINE"):
            layer = entity.dxf.layer
            if wall_layer_prefix and not layer.startswith(wall_layer_prefix):
                continue
            
            start = (entity.dxf.start.x, entity.dxf.start.y)
            end = (entity.dxf.end.x, entity.dxf.end.y)
            length = self._calculate_length(start, end)
            
            segment = WallSegment(
                id=self._generate_id(),
                layer=layer,
                entity_type="LINE",
                start_point=start,
                end_point=end,
                length=length
            )
            self.segments.append(segment)
        
        # 處理 LWPOLYLINE 實體 (輕量多段線，最常見)
        for entity in msp.query("LWPOLYLINE"):
            layer = entity.dxf.layer
            if wall_layer_prefix and not layer.startswith(wall_layer_prefix):
                continue
            
            # 取得所有頂點
            vertices = [(p[0], p[1]) for p in entity.get_points()]
            if len(vertices) < 2:
                continue
            
            length = self._calculate_polyline_length(vertices)
            
            segment = WallSegment(
                id=self._generate_id(),
                layer=layer,
                entity_type="LWPOLYLINE",
                start_point=vertices[0],
                end_point=vertices[-1],
                length=length,
                vertices=vertices
            )
            self.segments.append(segment)
        
        # 處理 POLYLINE 實體 (舊版多段線)
        for entity in msp.query("POLYLINE"):
            layer = entity.dxf.layer
            if wall_layer_prefix and not layer.startswith(wall_layer_prefix):
                continue
            
            vertices = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
            if len(vertices) < 2:
                continue
            
            length = self._calculate_polyline_length(vertices)
            
            segment = WallSegment(
                id=self._generate_id(),
                layer=layer,
                entity_type="POLYLINE",
                start_point=vertices[0],
                end_point=vertices[-1],
                length=length,
                vertices=vertices
            )
            self.segments.append(segment)
        
        # 處理 ARC 實體 (弧線)
        for entity in msp.query("ARC"):
            layer = entity.dxf.layer
            if wall_layer_prefix and not layer.startswith(wall_layer_prefix):
                continue
            
            try:
                # 取得弧線資訊
                center = (entity.dxf.center.x, entity.dxf.center.y)
                radius = entity.dxf.radius
                start_angle = math.radians(entity.dxf.start_angle)
                end_angle = math.radians(entity.dxf.end_angle)
                
                # 計算起點和終點
                start = (center[0] + radius * math.cos(start_angle),
                        center[1] + radius * math.sin(start_angle))
                end = (center[0] + radius * math.cos(end_angle),
                      center[1] + radius * math.sin(end_angle))
                
                # 計算弧長
                angle_diff = end_angle - start_angle
                if angle_diff < 0:
                    angle_diff += 2 * math.pi
                length = radius * angle_diff
                
                # 生成弧線的多邊形近似點（用於繪製）
                num_points = max(8, int(abs(angle_diff) / (math.pi / 16)))
                vertices = []
                for i in range(num_points + 1):
                    t = start_angle + (angle_diff * i / num_points)
                    vx = center[0] + radius * math.cos(t)
                    vy = center[1] + radius * math.sin(t)
                    vertices.append((vx, vy))
                
                segment = WallSegment(
                    id=self._generate_id(),
                    layer=layer,
                    entity_type="ARC",
                    start_point=start,
                    end_point=end,
                    length=length,
                    vertices=vertices
                )
                self.segments.append(segment)
            except Exception as e:
                print(f"  [!] 無法處理 ARC 實體: {e}")
        
        # 處理 CIRCLE 實體 (圓形) - 轉換為多邊形近似
        for entity in msp.query("CIRCLE"):
            layer = entity.dxf.layer
            if wall_layer_prefix and not layer.startswith(wall_layer_prefix):
                continue
            
            try:
                center = (entity.dxf.center.x, entity.dxf.center.y)
                radius = entity.dxf.radius
                
                # 計算圓周長
                length = 2 * math.pi * radius
                
                # 生成圓的多邊形近似點
                num_points = 32
                vertices = []
                for i in range(num_points + 1):
                    angle = 2 * math.pi * i / num_points
                    vx = center[0] + radius * math.cos(angle)
                    vy = center[1] + radius * math.sin(angle)
                    vertices.append((vx, vy))
                
                segment = WallSegment(
                    id=self._generate_id(),
                    layer=layer,
                    entity_type="CIRCLE",
                    start_point=vertices[0],
                    end_point=vertices[-1],
                    length=length,
                    vertices=vertices
                )
                self.segments.append(segment)
            except Exception as e:
                print(f"  [!] 無法處理 CIRCLE 實體: {e}")
        
        # 處理 SPLINE 實體 (樣條曲線)
        for entity in msp.query("SPLINE"):
            layer = entity.dxf.layer
            if wall_layer_prefix and not layer.startswith(wall_layer_prefix):
                continue
            
            try:
                # 取得控制點或計算點
                control_points = list(entity.control_points)
                if len(control_points) < 2:
                    continue
                
                vertices = [(p[0], p[1]) for p in control_points]
                length = self._calculate_polyline_length(vertices)
                
                segment = WallSegment(
                    id=self._generate_id(),
                    layer=layer,
                    entity_type="SPLINE",
                    start_point=vertices[0],
                    end_point=vertices[-1],
                    length=length,
                    vertices=vertices
                )
                self.segments.append(segment)
            except Exception as e:
                print(f"  [!] 無法處理 SPLINE 實體: {e}")
        
        # 處理 INSERT 實體 (圖塊引用) - 展開圖塊中的幾何
        insert_count = 0
        for entity in msp.query("INSERT"):
            layer = entity.dxf.layer
            if wall_layer_prefix and not layer.startswith(wall_layer_prefix):
                continue
            
            try:
                # 取得圖塊名稱和定義
                block_name = entity.dxf.name
                if block_name not in self.doc.blocks:
                    continue
                
                block = self.doc.blocks[block_name]
                
                # 取得變換參數
                insert_point = (entity.dxf.insert.x, entity.dxf.insert.y)
                x_scale = entity.dxf.xscale if hasattr(entity.dxf, 'xscale') else 1.0
                y_scale = entity.dxf.yscale if hasattr(entity.dxf, 'yscale') else 1.0
                rotation = math.radians(entity.dxf.rotation if hasattr(entity.dxf, 'rotation') else 0)
                
                # 遍歷圖塊中的實體
                for block_entity in block:
                    entity_type = block_entity.dxftype()
                    block_layer = block_entity.dxf.layer if hasattr(block_entity.dxf, 'layer') else layer
                    
                    # 如果圖塊實體的圖層是 "0"，使用 INSERT 的圖層
                    if block_layer == "0":
                        block_layer = layer
                    
                    if wall_layer_prefix and not block_layer.startswith(wall_layer_prefix):
                        continue
                    
                    if entity_type == "LINE":
                        start = self._transform_point(
                            (block_entity.dxf.start.x, block_entity.dxf.start.y),
                            insert_point, rotation, x_scale, y_scale
                        )
                        end = self._transform_point(
                            (block_entity.dxf.end.x, block_entity.dxf.end.y),
                            insert_point, rotation, x_scale, y_scale
                        )
                        length = self._calculate_length(start, end)
                        
                        segment = WallSegment(
                            id=self._generate_id(),
                            layer=block_layer,
                            entity_type="LINE",
                            start_point=start,
                            end_point=end,
                            length=length
                        )
                        self.segments.append(segment)
                        insert_count += 1
                    
                    elif entity_type == "LWPOLYLINE":
                        vertices = []
                        for p in block_entity.get_points():
                            tp = self._transform_point((p[0], p[1]), insert_point, rotation, x_scale, y_scale)
                            vertices.append(tp)
                        
                        if len(vertices) >= 2:
                            length = self._calculate_polyline_length(vertices)
                            segment = WallSegment(
                                id=self._generate_id(),
                                layer=block_layer,
                                entity_type="LWPOLYLINE",
                                start_point=vertices[0],
                                end_point=vertices[-1],
                                length=length,
                                vertices=vertices
                            )
                            self.segments.append(segment)
                            insert_count += 1
                    
                    elif entity_type == "ARC":
                        center = self._transform_point(
                            (block_entity.dxf.center.x, block_entity.dxf.center.y),
                            insert_point, rotation, x_scale, y_scale
                        )
                        radius = block_entity.dxf.radius * max(abs(x_scale), abs(y_scale))
                        start_angle = math.radians(block_entity.dxf.start_angle) + rotation
                        end_angle = math.radians(block_entity.dxf.end_angle) + rotation
                        
                        angle_diff = end_angle - start_angle
                        if angle_diff < 0:
                            angle_diff += 2 * math.pi
                        
                        num_points = max(8, int(abs(angle_diff) / (math.pi / 16)))
                        vertices = []
                        for i in range(num_points + 1):
                            t = start_angle + (angle_diff * i / num_points)
                            vx = center[0] + radius * math.cos(t)
                            vy = center[1] + radius * math.sin(t)
                            vertices.append((vx, vy))
                        
                        if len(vertices) >= 2:
                            length = radius * angle_diff
                            segment = WallSegment(
                                id=self._generate_id(),
                                layer=block_layer,
                                entity_type="ARC",
                                start_point=vertices[0],
                                end_point=vertices[-1],
                                length=length,
                                vertices=vertices
                            )
                            self.segments.append(segment)
                            insert_count += 1
                    
                    elif entity_type == "CIRCLE":
                        center = self._transform_point(
                            (block_entity.dxf.center.x, block_entity.dxf.center.y),
                            insert_point, rotation, x_scale, y_scale
                        )
                        radius = block_entity.dxf.radius * max(abs(x_scale), abs(y_scale))
                        
                        num_points = 32
                        vertices = []
                        for i in range(num_points + 1):
                            angle = 2 * math.pi * i / num_points
                            vx = center[0] + radius * math.cos(angle)
                            vy = center[1] + radius * math.sin(angle)
                            vertices.append((vx, vy))
                        
                        length = 2 * math.pi * radius
                        segment = WallSegment(
                            id=self._generate_id(),
                            layer=block_layer,
                            entity_type="CIRCLE",
                            start_point=vertices[0],
                            end_point=vertices[-1],
                            length=length,
                            vertices=vertices
                        )
                        self.segments.append(segment)
                        insert_count += 1
                        
            except Exception as e:
                print(f"  [!] 無法處理 INSERT 實體 '{entity.dxf.name}': {e}")
        
        if insert_count > 0:
            print(f"  從圖塊中展開了 {insert_count} 個幾何元素")
        
        print(f"\n提取到 {len(self.segments)} 條線段")
        return self.segments
    
    def summarize_by_layer(self) -> Dict[str, dict]:
        """按圖層統計牆長度"""
        summary = {}
        
        for seg in self.segments:
            if seg.layer not in summary:
                summary[seg.layer] = {
                    "layer": seg.layer,
                    "count": 0,
                    "total_length": 0.0,
                    "segments": []
                }
            
            summary[seg.layer]["count"] += 1
            summary[seg.layer]["total_length"] += seg.length
            summary[seg.layer]["segments"].append(seg.id)
        
        return summary
    
    def print_summary(self):
        """印出統計摘要"""
        summary = self.summarize_by_layer()
        
        print("\n" + "=" * 60)
        print("牆長度統計摘要")
        print("=" * 60)
        
        total_length = 0
        total_count = 0
        
        for layer, data in sorted(summary.items()):
            length_m = data["total_length"] / 1000  # 假設單位是 mm，轉換成 m
            print(f"\n{layer}:")
            print(f"  線段數量: {data['count']}")
            print(f"  總長度: {data['total_length']:.2f} mm ({length_m:.2f} m)")
            total_length += data["total_length"]
            total_count += data["count"]
        
        print("\n" + "-" * 60)
        print(f"總計: {total_count} 條線段, {total_length:.2f} mm ({total_length/1000:.2f} m)")
        print("=" * 60)
    
    def export_to_json(self, output_path: str):
        """匯出為 JSON 格式（供前端使用）"""
        data = {
            "source_file": self.filepath,
            "dimscale": self.dimscale,
            "insunits": self.insunits,
            "layers": self.layers,
            "segments": [seg.to_dict() for seg in self.segments],
            "summary": self.summarize_by_layer()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ 已匯出 JSON: {output_path}")


def main():
    # 測試用範例檔案
    parser = DXFParser("/home/claude/wall-quantity-calculator/sample_floor_plan.dxf")
    
    if parser.load():
        parser.extract_layers()
        parser.extract_wall_entities(wall_layer_prefix="A-WALL")
        parser.print_summary()
        parser.export_to_json("/home/claude/wall-quantity-calculator/parsed_data.json")


if __name__ == "__main__":
    main()
