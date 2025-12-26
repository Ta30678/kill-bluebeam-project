# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Wall Quantity Calculator (牆量計算工具) - A Python/Flask web application that replaces Bluebeam for calculating wall quantities from DXF architectural floor plans.

### Background & Pain Points
現有工作流程問題：
- AutoCAD → PDF 轉檔 → Bluebeam 手動拉線測量
- 需人工對照建築圖（有牆無梁）與結構圖（有梁無牆）判斷牆類型
- 每個案子分類系統不同，無法固定化
- PDF 轉換遺失圖層資訊

### Goals
- DXF 為主要輸入（保留圖層資訊）
- 依圖層自動初步分類，可手動調整
- 輸出 CSV 統計表匯入公司試算表
- 同事務所案子可複用圖層對應設定

## Real-World Workflow（實際工作流程）

### 資料來源時序
1. **建築底圖**（第一波）- 可能是唯一可用資料
2. **結構平面圖**（第二/三波）- 需等 ETABS 分析完成
   - 結構圖用建築圖當底圖，結構配置畫在上面
   - 建築底圖會合併成單一圖層
   - 質量計算常在結構圖完成前就需進行

### 兩種使用模式
| 模式 | 條件 | 功能 |
|------|------|------|
| **簡化模式（核心）** | 僅建築圖 | 依圖層分類 + 手動編輯調整 |
| 完整模式 | 有結構圖 | 疊圖判斷梁下/版下（增強功能） |

### 為什麼需要高度自由化編輯
- 質量計算常在結構圖完成前進行
- 無法自動判斷梁下/版下時，需人工介入
- 每案分類系統不同

## 分棟分樓層架構

### 資料階層
```
專案 (Project)
  └─ 結構物/棟 (Building)
       └─ 樓層 (Floor)
            └─ 牆類型 (Wall Category)
                 └─ 線段 (Segments)
```

### 統計範圍
- **地下層**：全棟共用，一起統計
- **地上層**：分棟分樓層統計（例：6 個結構物各自統計）
- 支援匯總與分項匯出

### 樓層命名範例
標準層可合併（如 7~8F, 9~12F），特殊層單獨（R1F, R2~PRF）

## Common Commands

```bash
# Install dependencies
pip install flask flask-cors ezdxf werkzeug

# Run the web server (serves on http://localhost:5000)
python app.py

# Create a simple test DXF file for development
python create_test_dxf.py

# Test DXF parsing (update file paths in script first)
python test_dxf.py

# Test with local DXF files
python test_local_dxf.py

# Test with real DXF files
python test_real_dxf.py

# Test database structure with sample data
python test_database.py

# Test API endpoints
python test_api.py
```

**File Path Notes**:
- Code may contain hardcoded Linux paths like `/home/claude/wall-quantity-calculator/`
- When working on Windows, use relative paths or `os.path.join()` for cross-platform compatibility
- Test DXF files may be in `建築底圖test/` directory
- Uploaded files are stored in `uploads/` directory (auto-created)
- Database file: `wall_calculator.db` (or `test_wall_calculator.db` for tests)

## Architecture

**Backend (Python/Flask)**
- [app.py](app.py) - Flask REST API server. Serves the frontend and provides endpoints for project CRUD, DXF upload/parsing, wall segment management, and CSV export.
- [database.py](database.py) - SQLite database manager with `DatabaseManager` class. Handles hierarchical data (Project → Building → Floor → Wall Category → Segments).
- [dxf_parser.py](dxf_parser.py) - DXF file parser using `ezdxf` library. Extracts LINE, LWPOLYLINE, POLYLINE entities and calculates lengths. Uses `WallSegment` dataclass. Includes multi-encoding support (UTF-8, CP950, GBK, auto-recovery mode) for handling files from different CAD systems.

**Frontend**
- [index.html](index.html) - Single-page application with Canvas-based drawing engine for visualizing/selecting wall segments. Supports pan, zoom, multi-select (Shift+click), and category assignment.

## Database Schema

### Core Tables
| Table | Purpose |
|-------|---------|
| projects | 每個 DXF 檔案對應一個專案 |
| buildings | 結構物/棟別（支援地下層與地上層分棟） |
| floors | 樓層資訊（支援合併樓層如 7~8F） |
| wall_categories | 使用者自訂的牆類型（含高度公式） |
| layer_mappings | DXF 圖層 → 牆類型對應（可複用） |
| wall_segments | 解析出的牆線段（座標、長度、分類） |
| edit_history | 編輯歷史，用於 Undo/Redo |

**Note**: Buildings and floors tables are implemented but not yet integrated with the API endpoints.

## Domain Knowledge

### Wall Classification System
分類維度：位置類型 × 高度類型
- **位置類型**：室內/室外/梁下/版下/陽台/水箱牆
- **高度類型**：樓高-梁深 / 同樓高 / 固定高度（如 1.5m 女兒牆）

### 建築圖 vs 結構圖
- 建築圖：有牆無梁（A-WALL 圖層）
- 結構圖：有梁無牆
- 需疊合比對判斷牆在梁下或版下

### 結構平面圖組成
- 建築底圖（通常合併為單一圖層，藍色）
- 結構配置：梁（黃/綠線）、柱、剪力牆（紅色標註"剪力牆"）
- 疊圖顯示可判斷牆與梁的相對位置

### DXF Layer Convention
- 預設提取 `A-WALL` 開頭的圖層（建築圖層命名慣例）
- 圖層命名需與事務所確認

## API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/upload` | Upload DXF file |
| POST | `/api/parse` | Parse DXF and create project |
| GET/POST | `/api/projects` | List/create projects |
| GET | `/api/projects/<id>/segments` | Get wall segments |
| PUT | `/api/segments/<id>/category` | Update segment classification |
| GET | `/api/projects/<id>/summary` | Get length statistics |
| GET | `/api/projects/<id>/export/csv` | Export CSV |

## Development Status

### ✅ Completed Backend
- **DXF Parser**:
  - LINE, LWPOLYLINE, POLYLINE, ARC, CIRCLE, SPLINE entities
  - INSERT (block) expansion with transformations
  - Multi-encoding support (UTF-8, CP950, GBK, auto-recovery mode)
  - Length calculation for all entity types
  - Successfully tested with 138MB files (118,642 segments)
- **Database**: Full SQLite schema with buildings/floors hierarchy
- **Flask API**: Complete REST API with all CRUD endpoints
- **Statistics**: Summary queries by project/building/floor

### ⚠️ Partial Implementation
- **Buildings/Floors API**: Endpoints exist but not integrated with frontend
- **Canvas Interface**: Basic structure exists, drawing not implemented

### ❌ Not Yet Implemented
1. **Frontend Canvas Drawing**: Rendering DXF segments on canvas
2. **Layer Mapping UI**: Visual interface for DXF layer → category assignment
3. **Layer Selection**: UI for selecting which layers to calculate
4. **Undo/Redo**: Using edit_history table
5. **Overlay Feature**: Architectural + structural drawing overlay
6. **Height Formula Calculation**: Volume calculation (length × height × thickness)
7. **CSV Export**: Frontend integration with export endpoint

## Performance Considerations

- **Canvas 渲染**：批次渲染避免逐條繪製，O(n) → O(1)
- **大型 DXF**：ezdxf 支援 lazy loading，避免重複讀取
- **SQLite 索引**：`CREATE INDEX idx_line_project ON wall_segments(project_id, category_id)`
- **LOD**：超過 10,000 線段時考慮 Level of Detail

## Bluebeam vs This Tool

| 功能 | Bluebeam (舊) | 本工具 (新) |
|------|--------------|------------|
| 輸入格式 | PDF（圖層遺失） | DXF（圖層保留） |
| 測量方式 | 手動拉線 | 自動解析幾何 |
| 分類邏輯 | 人工判斷 | 圖層映射 + 手動調整 |
| 資料輸出 | 手動輸入試算表 | CSV 自動匯入 |
| 可複用性 | 每案重來 | 圖層對應可複用 |

## Important Notes

### File Paths and Environment
- Code contains hardcoded Linux paths like `/home/claude/wall-quantity-calculator/`
- **When working on Windows**: Use `os.path.join(os.getcwd(), ...)` for cross-platform compatibility
- Uploaded DXF files: `uploads/` directory (auto-created)
- Database file: `wall_calculator.db` (or `test_wall_calculator.db` for tests)
- Test DXF files may be in `建築底圖test/` directory

### DXF Encoding Support
The parser includes robust encoding handling for files from different CAD systems:
- Attempts multiple encodings: default → UTF-8 → CP950 (Traditional Chinese) → GBK (Simplified Chinese) → auto-recovery
- Successfully handles files from various sources and AutoCAD versions
- If parsing fails, suggests using ODA File Converter or AutoCAD to re-save as DXF 2018 format

### Testing
- [create_test_dxf.py](create_test_dxf.py) - Creates a simple test DXF with A-WALL-EXT, A-WALL-INT, A-WALL-RC layers
- [test_dxf.py](test_dxf.py) - Generic DXF parsing test (update file paths)
- [test_local_dxf.py](test_local_dxf.py) - Tests with local DXF files
- [test_real_dxf.py](test_real_dxf.py) - Tests with real project files
- [test_database.py](test_database.py) - Demonstrates building/floor hierarchy
- [test_api.py](test_api.py) - API endpoint testing

**Tested Successfully**:
- Small files (20KB, 6 segments): ✅
- Medium files (95MB, 25,726 segments, 441 layers): ✅
- Large files (138MB, 118,642 segments): ✅

### Project Structure
- The `claude skills/` directory contains unrelated Claude AI skill examples (ignore this)
- Frontend is a single HTML file at [index.html](index.html) - no build step required
- [index-ref.html](index-ref.html) may be a reference implementation

### Core Design Principles
- **無結構圖也能完整使用**：Tool functions fully without structural drawings; overlay is optional enhancement
- **圖層為主要分類依據**：Layer-based classification is primary, manual adjustment is secondary
- **資料可複用**：Layer mappings can be reused across projects from the same architecture firm

### Known Limitations
- Frontend drawing not yet implemented - canvas is blank after upload
- Layer selection UI not yet implemented
- CSV export button exists but functionality incomplete
- Statistics display on frontend needs implementation
