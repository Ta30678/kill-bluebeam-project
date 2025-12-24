"""
SQLite Database Manager for Wall Quantity Calculator
管理專案、牆類型對應、線段資料的儲存與讀取
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from pathlib import Path

class DatabaseManager:
    """SQLite 資料庫管理器"""
    
    def __init__(self, db_path: str = "wall_calculator.db"):
        self.db_path = db_path
        self.conn = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """建立資料庫連線"""
        # 使用 check_same_thread=False 允許多線程使用（Flask 會自動處理並發）
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 讓查詢結果可以用欄位名稱存取
        print(f"[OK] 已連接資料庫: {self.db_path}")
    
    def _create_tables(self):
        """建立資料表結構"""
        cursor = self.conn.cursor()
        
        # 專案表 - 每個 DXF 檔案對應一個專案
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                source_file TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)

        # 結構物/棟別表 - 一個專案可包含多棟建築物
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                building_code TEXT NOT NULL,
                building_name TEXT NOT NULL,
                is_basement INTEGER DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, building_code)
            )
        """)

        # 樓層表 - 每棟建築可包含多個樓層
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS floors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_id INTEGER NOT NULL,
                floor_code TEXT NOT NULL,
                floor_name TEXT NOT NULL,
                floor_level INTEGER,
                is_combined INTEGER DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (building_id) REFERENCES buildings(id) ON DELETE CASCADE,
                UNIQUE(building_id, floor_code)
            )
        """)

        # 牆類型定義表 - 使用者可自訂的分類系統
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wall_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                category_code TEXT NOT NULL,
                category_name TEXT NOT NULL,
                height_type TEXT,
                height_formula TEXT,
                color TEXT DEFAULT '#888888',
                line_weight REAL DEFAULT 1.0,
                display_order INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                UNIQUE(project_id, category_code)
            )
        """)
        
        # 圖層對應表 - DXF 圖層 → 牆類型的對應關係
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS layer_mappings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                dxf_layer_name TEXT NOT NULL,
                category_id INTEGER,
                auto_detected INTEGER DEFAULT 0,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (category_id) REFERENCES wall_categories(id) ON DELETE SET NULL,
                UNIQUE(project_id, dxf_layer_name)
            )
        """)
        
        # 線段表 - 儲存所有解析出的牆線段
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wall_segments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                floor_id INTEGER,
                segment_uid TEXT NOT NULL,
                dxf_layer TEXT NOT NULL,
                category_id INTEGER,
                entity_type TEXT NOT NULL,
                start_x REAL NOT NULL,
                start_y REAL NOT NULL,
                end_x REAL NOT NULL,
                end_y REAL NOT NULL,
                length REAL NOT NULL,
                vertices_json TEXT,
                is_modified INTEGER DEFAULT 0,
                notes TEXT,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (floor_id) REFERENCES floors(id) ON DELETE SET NULL,
                FOREIGN KEY (category_id) REFERENCES wall_categories(id) ON DELETE SET NULL,
                UNIQUE(project_id, segment_uid)
            )
        """)
        
        # 編輯歷史表 - 追蹤使用者的編輯操作 (可選)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS edit_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                segment_id INTEGER,
                action TEXT NOT NULL,
                old_value TEXT,
                new_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
                FOREIGN KEY (segment_id) REFERENCES wall_segments(id) ON DELETE CASCADE
            )
        """)
        
        self.conn.commit()
        print("[OK] 資料表結構已建立")
    
    # ==================== 專案管理 ====================
    
    def create_project(self, name: str, source_file: str = None, notes: str = None) -> int:
        """建立新專案，回傳專案 ID"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO projects (name, source_file, notes) VALUES (?, ?, ?)",
            (name, source_file, notes)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_project(self, project_id: int) -> Optional[dict]:
        """取得專案資訊"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def list_projects(self) -> List[dict]:
        """列出所有專案"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
        return [dict(row) for row in cursor.fetchall()]

    # ==================== 結構物/棟別管理 ====================

    def add_building(self, project_id: int, code: str, name: str,
                     is_basement: bool = False, display_order: int = 0) -> int:
        """新增結構物/棟別"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO buildings
            (project_id, building_code, building_name, is_basement, display_order)
            VALUES (?, ?, ?, ?, ?)
        """, (project_id, code, name, 1 if is_basement else 0, display_order))
        self.conn.commit()
        return cursor.lastrowid

    def get_buildings(self, project_id: int) -> List[dict]:
        """取得專案的所有結構物/棟別"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM buildings WHERE project_id = ? ORDER BY display_order",
            (project_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def update_building(self, building_id: int, **kwargs) -> bool:
        """更新結構物/棟別資訊"""
        allowed_fields = ['building_code', 'building_name', 'is_basement', 'display_order', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE buildings SET {set_clause} WHERE id = ?",
            (*updates.values(), building_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    # ==================== 樓層管理 ====================

    def add_floor(self, building_id: int, code: str, name: str,
                  floor_level: int = None, is_combined: bool = False,
                  display_order: int = 0) -> int:
        """新增樓層"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO floors
            (building_id, floor_code, floor_name, floor_level, is_combined, display_order)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (building_id, code, name, floor_level, 1 if is_combined else 0, display_order))
        self.conn.commit()
        return cursor.lastrowid

    def get_floors(self, building_id: int) -> List[dict]:
        """取得棟別的所有樓層"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM floors WHERE building_id = ? ORDER BY display_order",
            (building_id,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_all_floors_by_project(self, project_id: int) -> List[dict]:
        """取得專案的所有樓層（含棟別資訊）"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT f.*, b.building_code, b.building_name, b.is_basement
            FROM floors f
            JOIN buildings b ON f.building_id = b.id
            WHERE b.project_id = ?
            ORDER BY b.display_order, f.display_order
        """, (project_id,))
        return [dict(row) for row in cursor.fetchall()]

    def update_floor(self, floor_id: int, **kwargs) -> bool:
        """更新樓層資訊"""
        allowed_fields = ['floor_code', 'floor_name', 'floor_level', 'is_combined', 'display_order', 'notes']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return False

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE floors SET {set_clause} WHERE id = ?",
            (*updates.values(), floor_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0

    # ==================== 牆類型管理 ====================
    
    def add_wall_category(self, project_id: int, code: str, name: str, 
                          height_type: str = None, height_formula: str = None,
                          color: str = "#888888", line_weight: float = 1.0) -> int:
        """新增牆類型"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO wall_categories 
            (project_id, category_code, category_name, height_type, height_formula, color, line_weight)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (project_id, code, name, height_type, height_formula, color, line_weight))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_categories(self, project_id: int) -> List[dict]:
        """取得專案的所有牆類型"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM wall_categories WHERE project_id = ? ORDER BY display_order",
            (project_id,)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def update_category(self, category_id: int, **kwargs) -> bool:
        """更新牆類型"""
        allowed_fields = ['category_code', 'category_name', 'height_type', 
                         'height_formula', 'color', 'line_weight', 'display_order']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False
        
        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        cursor = self.conn.cursor()
        cursor.execute(
            f"UPDATE wall_categories SET {set_clause} WHERE id = ?",
            (*updates.values(), category_id)
        )
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ==================== 圖層對應管理 ====================
    
    def set_layer_mapping(self, project_id: int, dxf_layer: str, category_id: int = None):
        """設定或更新圖層對應"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO layer_mappings (project_id, dxf_layer_name, category_id)
            VALUES (?, ?, ?)
            ON CONFLICT(project_id, dxf_layer_name) 
            DO UPDATE SET category_id = excluded.category_id
        """, (project_id, dxf_layer, category_id))
        self.conn.commit()
    
    def get_layer_mappings(self, project_id: int) -> Dict[str, Optional[int]]:
        """取得圖層對應關係 (圖層名稱 → 類型ID)"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT dxf_layer_name, category_id FROM layer_mappings WHERE project_id = ?",
            (project_id,)
        )
        return {row['dxf_layer_name']: row['category_id'] for row in cursor.fetchall()}
    
    # ==================== 線段管理 ====================
    
    def import_segments(self, project_id: int, segments: List[dict], floor_id: int = None) -> int:
        """批次匯入線段資料"""
        cursor = self.conn.cursor()
        count = 0

        # 先取得圖層對應
        mappings = self.get_layer_mappings(project_id)

        for seg in segments:
            category_id = mappings.get(seg.get('layer'))
            vertices_json = json.dumps(seg.get('vertices')) if seg.get('vertices') else None

            try:
                cursor.execute("""
                    INSERT INTO wall_segments
                    (project_id, floor_id, segment_uid, dxf_layer, category_id, entity_type,
                     start_x, start_y, end_x, end_y, length, vertices_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    project_id,
                    floor_id,
                    seg['id'],
                    seg['layer'],
                    category_id,
                    seg['entity_type'],
                    seg['start_point'][0],
                    seg['start_point'][1],
                    seg['end_point'][0],
                    seg['end_point'][1],
                    seg['length'],
                    vertices_json
                ))
                count += 1
            except sqlite3.IntegrityError:
                # 重複的線段 UID，跳過
                pass

        self.conn.commit()
        return count
    
    def get_segments(self, project_id: int, category_id: int = None) -> List[dict]:
        """取得線段資料，可依類型篩選"""
        cursor = self.conn.cursor()
        
        if category_id is not None:
            cursor.execute("""
                SELECT ws.*, wc.category_name, wc.color
                FROM wall_segments ws
                LEFT JOIN wall_categories wc ON ws.category_id = wc.id
                WHERE ws.project_id = ? AND ws.category_id = ?
            """, (project_id, category_id))
        else:
            cursor.execute("""
                SELECT ws.*, wc.category_name, wc.color
                FROM wall_segments ws
                LEFT JOIN wall_categories wc ON ws.category_id = wc.id
                WHERE ws.project_id = ?
            """, (project_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_segment_category(self, segment_id: int, category_id: int, 
                                 record_history: bool = True) -> bool:
        """更新線段的分類"""
        cursor = self.conn.cursor()
        
        if record_history:
            # 記錄編輯歷史
            cursor.execute(
                "SELECT project_id, category_id FROM wall_segments WHERE id = ?", 
                (segment_id,)
            )
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    INSERT INTO edit_history (project_id, segment_id, action, old_value, new_value)
                    VALUES (?, ?, 'change_category', ?, ?)
                """, (row['project_id'], segment_id, str(row['category_id']), str(category_id)))
        
        cursor.execute("""
            UPDATE wall_segments 
            SET category_id = ?, is_modified = 1 
            WHERE id = ?
        """, (category_id, segment_id))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    # ==================== 統計查詢 ====================
    
    def get_summary(self, project_id: int) -> List[dict]:
        """取得專案的牆長度統計"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 
                wc.id as category_id,
                wc.category_code,
                wc.category_name,
                wc.color,
                wc.height_type,
                wc.height_formula,
                COUNT(ws.id) as segment_count,
                COALESCE(SUM(ws.length), 0) as total_length
            FROM wall_categories wc
            LEFT JOIN wall_segments ws ON wc.id = ws.category_id AND ws.project_id = wc.project_id
            WHERE wc.project_id = ?
            GROUP BY wc.id
            ORDER BY wc.display_order
        """, (project_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_uncategorized_summary(self, project_id: int) -> dict:
        """取得未分類線段的統計"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                dxf_layer,
                COUNT(*) as segment_count,
                SUM(length) as total_length
            FROM wall_segments
            WHERE project_id = ? AND category_id IS NULL
            GROUP BY dxf_layer
        """, (project_id,))

        return [dict(row) for row in cursor.fetchall()]

    def get_summary_by_floor(self, project_id: int, floor_id: int) -> List[dict]:
        """取得指定樓層的牆長度統計"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                wc.id as category_id,
                wc.category_code,
                wc.category_name,
                wc.color,
                wc.height_type,
                wc.height_formula,
                COUNT(ws.id) as segment_count,
                COALESCE(SUM(ws.length), 0) as total_length
            FROM wall_categories wc
            LEFT JOIN wall_segments ws ON wc.id = ws.category_id AND ws.floor_id = ?
            WHERE wc.project_id = ?
            GROUP BY wc.id
            ORDER BY wc.display_order
        """, (floor_id, project_id))

        return [dict(row) for row in cursor.fetchall()]

    def get_summary_by_building(self, project_id: int, building_id: int) -> List[dict]:
        """取得指定棟別的牆長度統計（所有樓層合計）"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                wc.id as category_id,
                wc.category_code,
                wc.category_name,
                wc.color,
                wc.height_type,
                wc.height_formula,
                COUNT(ws.id) as segment_count,
                COALESCE(SUM(ws.length), 0) as total_length
            FROM wall_categories wc
            LEFT JOIN wall_segments ws ON wc.id = ws.category_id
            LEFT JOIN floors f ON ws.floor_id = f.id
            WHERE wc.project_id = ? AND f.building_id = ?
            GROUP BY wc.id
            ORDER BY wc.display_order
        """, (project_id, building_id))

        return [dict(row) for row in cursor.fetchall()]

    def get_full_hierarchy_summary(self, project_id: int) -> dict:
        """取得完整的分棟分樓層統計"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT
                b.id as building_id,
                b.building_code,
                b.building_name,
                b.is_basement,
                f.id as floor_id,
                f.floor_code,
                f.floor_name,
                wc.id as category_id,
                wc.category_code,
                wc.category_name,
                wc.color,
                COUNT(ws.id) as segment_count,
                COALESCE(SUM(ws.length), 0) as total_length
            FROM buildings b
            LEFT JOIN floors f ON b.id = f.building_id
            LEFT JOIN wall_segments ws ON f.id = ws.floor_id
            LEFT JOIN wall_categories wc ON ws.category_id = wc.id
            WHERE b.project_id = ?
            GROUP BY b.id, f.id, wc.id
            ORDER BY b.display_order, f.display_order, wc.display_order
        """, (project_id,))

        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """關閉資料庫連線"""
        if self.conn:
            self.conn.close()
            print("[OK] 資料庫連線已關閉")


def demo():
    """示範資料庫操作流程"""
    import json
    
    # 初始化資料庫
    db = DatabaseManager("/home/claude/wall-quantity-calculator/wall_calculator.db")
    
    # 建立專案
    project_id = db.create_project(
        name="示範專案 - 住宅大樓 A 棟",
        source_file="sample_floor_plan.dxf",
        notes="這是一個示範專案"
    )
    print(f"\n[OK] 已建立專案 ID: {project_id}")
    
    # 建立牆類型
    categories = [
        ("EXT", "外牆", "樓高-梁深", "floor_height - beam_depth", "#E74C3C"),
        ("INT", "內牆", "樓高-梁深", "floor_height - beam_depth", "#F1C40F"),
        ("RC", "RC牆", "同樓高", "floor_height", "#1ABC9C"),
        ("PART", "輕隔間", "樓高-梁深", "floor_height - beam_depth", "#2ECC71"),
        ("BALC", "陽台牆", "1.2m", "1200", "#9B59B6"),
        ("WATER", "水箱牆", "依設計", "custom", "#3498DB"),
        ("PARAPET", "女兒牆", "1.5m", "1500", "#E67E22"),
    ]
    
    category_ids = {}
    for code, name, height_type, formula, color in categories:
        cat_id = db.add_wall_category(
            project_id, code, name, height_type, formula, color
        )
        category_ids[f"A-WALL-{code}"] = cat_id
    
    print(f"[OK] 已建立 {len(categories)} 個牆類型")

    # 設定圖層對應
    for layer_name, cat_id in category_ids.items():
        db.set_layer_mapping(project_id, layer_name, cat_id)

    print("[OK] 已設定圖層對應")

    # 載入解析後的 JSON 資料
    with open("/home/claude/wall-quantity-calculator/parsed_data.json", 'r') as f:
        parsed_data = json.load(f)

    # 匯入線段
    count = db.import_segments(project_id, parsed_data['segments'])
    print(f"[OK] 已匯入 {count} 條線段")
    
    # 輸出統計
    print("\n" + "=" * 60)
    print("牆長度統計（按類型）")
    print("=" * 60)
    
    for row in db.get_summary(project_id):
        length_m = row['total_length'] / 1000
        print(f"\n{row['category_name']} ({row['category_code']}):")
        print(f"  線段數: {row['segment_count']}")
        print(f"  總長度: {row['total_length']:.2f} mm ({length_m:.2f} m)")
        print(f"  高度類型: {row['height_type']}")
        print(f"  高度公式: {row['height_formula']}")
    
    # 檢查未分類
    uncategorized = db.get_uncategorized_summary(project_id)
    if uncategorized:
        print("\n⚠ 未分類的線段:")
        for row in uncategorized:
            print(f"  {row['dxf_layer']}: {row['segment_count']} 條")
    
    print("\n" + "=" * 60)
    
    db.close()


if __name__ == "__main__":
    demo()
