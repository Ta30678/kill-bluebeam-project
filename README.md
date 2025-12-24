# 牆量計算工具 (Wall Quantity Calculator)

取代 Blueberry 的現代化牆量計算工作流程。

## 專案目標

從 DXF 建築平面圖中自動識別牆線段，並依據使用者定義的分類系統進行歸類，最終輸出各類型牆的長度統計表。

## 專案結構

```
wall-quantity-calculator/
├── app.py                 # Flask API 後端
├── database.py            # SQLite 資料庫管理
├── dxf_parser.py          # DXF 檔案解析器
├── create_sample_dxf.py   # 範例 DXF 生成器（測試用）
├── requirements.txt       # Python 依賴
├── wall_calculator.db     # SQLite 資料庫檔案
├── parsed_data.json       # 解析後的 JSON 資料
├── uploads/               # 上傳檔案暫存目錄
└── frontend/
    └── index.html         # 前端介面
```

## 安裝與執行

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 執行範例（測試資料庫）

```bash
# 生成範例 DXF 檔案
python create_sample_dxf.py

# 解析 DXF 並查看結果
python dxf_parser.py

# 建立示範專案並匯入資料庫
python database.py
```

### 3. 啟動 Web 伺服器

```bash
python app.py
```

然後在瀏覽器開啟 `http://localhost:5000`

## 核心功能

### DXF 解析器 (`dxf_parser.py`)

- 讀取 DXF 檔案（使用 ezdxf 函式庫）
- 提取所有圖層資訊
- 提取 LINE、LWPOLYLINE、POLYLINE 等幾何實體
- 計算每條線段的長度
- 匯出為 JSON 格式

### 資料庫結構 (`database.py`)

**projects** - 專案表
- 每個 DXF 檔案對應一個專案

**wall_categories** - 牆類型定義表
- 使用者可自訂的分類系統
- 包含類型代碼、名稱、高度公式、顏色等

**layer_mappings** - 圖層對應表
- DXF 圖層名稱 → 牆類型的對應關係
- 可複用於相同建築師事務所的案子

**wall_segments** - 線段表
- 儲存所有解析出的牆線段
- 可編輯分類

**edit_history** - 編輯歷史表
- 追蹤使用者的編輯操作

### API 端點 (`app.py`)

| 方法 | 端點 | 說明 |
|------|------|------|
| GET | `/api/projects` | 列出所有專案 |
| POST | `/api/projects` | 建立新專案 |
| GET | `/api/projects/<id>` | 取得專案詳情 |
| POST | `/api/upload` | 上傳 DXF 檔案 |
| POST | `/api/parse` | 解析 DXF 並建立專案 |
| GET | `/api/projects/<id>/categories` | 取得牆類型 |
| POST | `/api/projects/<id>/categories` | 新增牆類型 |
| GET | `/api/projects/<id>/segments` | 取得線段資料 |
| PUT | `/api/segments/<id>/category` | 更新線段分類 |
| GET | `/api/projects/<id>/summary` | 取得統計摘要 |
| GET | `/api/projects/<id>/export/csv` | 匯出 CSV |

### 前端介面 (`frontend/index.html`)

- Canvas 繪圖引擎，支援平移、縮放
- 線段選取與多選（Shift + 點擊）
- 即時分類更新
- 統計摘要表

## 工作流程

1. **上傳 DXF** → 檔案儲存到 `uploads/` 目錄
2. **解析 DXF** → 提取圖層和幾何實體
3. **建立專案** → 資料存入 SQLite
4. **定義牆類型** → 使用者自訂分類系統
5. **設定圖層對應** → DXF 圖層 → 牆類型
6. **自動分類** → 依對應規則批次分類
7. **人工校正** → 視覺化編輯器調整
8. **匯出統計** → CSV 格式供試算表使用

## 技術選型

- **後端**: Python + Flask
- **資料庫**: SQLite（輕量、單檔、零配置）
- **DXF 解析**: ezdxf（功能完整、積極維護）
- **前端**: Vanilla JavaScript + Canvas（無框架依賴）

## 未來擴充

- [ ] 結構平面圖疊合顯示
- [ ] 梁位置自動偵測
- [ ] 批次專案處理
- [ ] 高度公式自動計算面積
- [ ] 匯出至 Excel 含公式
- [ ] 多人協作（WebSocket）

## 與 Blueberry 的差異

| 功能 | Blueberry | 本工具 |
|------|-----------|--------|
| 輸入格式 | PDF | DXF（保留圖層資訊）|
| 自動分類 | 無 | 依圖層自動對應 |
| 分類系統 | 固定 | 每案自訂 |
| 資料儲存 | 專有格式 | SQLite + JSON |
| 統計匯出 | 內建表格 | CSV（可匯入試算表）|
| 可擴充性 | 低 | 高（API 架構）|

---

## 開發筆記

這個專案是為了取代現有的 CAD → PDF → Blueberry 工作流程而設計的。主要改善點：

1. **保留 DXF 圖層資訊**：避免 PDF 轉換時遺失語意資訊
2. **自訂分類系統**：每個案子可以有自己的牆類型定義
3. **可編輯性**：所有分類都可以事後調整
4. **流暢操作**：Canvas 繪圖引擎確保大量線段的流暢渲染

建議的下一步開發：

1. 完善 DXF 上傳和解析流程
2. 實作圖層對應的 UI
3. 支援結構圖疊合
4. 加入 undo/redo 功能
