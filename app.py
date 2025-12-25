"""
Flask API Backend for Wall Quantity Calculator
提供 RESTful API 供前端使用
"""
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from database import DatabaseManager
from dxf_parser import DXFParser

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app)

# 設定
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
DB_PATH = os.path.join(os.getcwd(), 'wall_calculator.db')
ALLOWED_EXTENSIONS = {'dxf', 'dwg'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max (支援大型 DXF 檔案)

# 資料庫實例
db = DatabaseManager(DB_PATH)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== 靜態頁面 ====================

@app.route('/')
def index():
    # 直接返回當前目錄下的 index.html
    return send_from_directory('.', 'index.html')


# ==================== 專案 API ====================

@app.route('/api/projects', methods=['GET'])
def list_projects():
    """列出所有專案"""
    projects = db.list_projects()
    return jsonify({"success": True, "data": projects})


@app.route('/api/projects', methods=['POST'])
def create_project():
    """建立新專案"""
    data = request.json
    project_id = db.create_project(
        name=data.get('name', '未命名專案'),
        source_file=data.get('source_file'),
        notes=data.get('notes')
    )
    return jsonify({"success": True, "project_id": project_id})


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """取得專案詳細資訊"""
    project = db.get_project(project_id)
    if not project:
        return jsonify({"success": False, "error": "專案不存在"}), 404
    
    # 同時回傳統計資料
    summary = db.get_summary(project_id)
    uncategorized = db.get_uncategorized_summary(project_id)
    
    return jsonify({
        "success": True,
        "data": {
            "project": project,
            "summary": summary,
            "uncategorized": uncategorized
        }
    })


# ==================== 檔案上傳與解析 ====================

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上傳 DXF 檔案"""
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "沒有選擇檔案"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "沒有選擇檔案"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"success": False, "error": "不支援的檔案格式"}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    return jsonify({
        "success": True,
        "filename": filename,
        "filepath": filepath
    })


@app.route('/api/parse', methods=['POST'])
def parse_dxf():
    """解析 DXF 檔案並建立專案"""
    data = request.json
    filepath = data.get('filepath')
    project_name = data.get('project_name', '未命名專案')
    selected_layers = data.get('selected_layers', None)  # 使用者選擇的圖層列表

    if not filepath or not os.path.exists(filepath):
        return jsonify({"success": False, "error": "檔案不存在"}), 400

    # 解析 DXF
    parser = DXFParser(filepath)
    if not parser.load():
        return jsonify({"success": False, "error": "無法解析 DXF 檔案"}), 400

    # 提取圖層資訊
    layers = parser.extract_layers()

    # 提取所有線段（用於顯示完整平面圖）
    all_segments = parser.extract_wall_entities(wall_layer_prefix=None)

    # 建立專案
    project_id = db.create_project(
        name=project_name,
        source_file=os.path.basename(filepath)
    )

    # 匯入所有線段到資料庫
    segment_dicts = [seg.to_dict() for seg in all_segments]
    count = db.import_segments(project_id, segment_dicts)

    # 如果使用者有選擇特定圖層，標記這些圖層的線段
    selected_segment_count = 0
    if selected_layers:
        selected_segments = [seg for seg in all_segments if seg.layer in selected_layers]
        selected_segment_count = len(selected_segments)

    return jsonify({
        "success": True,
        "project_id": project_id,
        "layers": layers,  # 所有圖層資訊
        "dimscale": parser.dimscale,  # DXF DIMSCALE (尺寸縮放比例)
        "insunits": parser.insunits,  # DXF INSUNITS (插入單位)
        "total_segment_count": count,  # 總線段數
        "selected_segment_count": selected_segment_count,  # 選中的線段數
        "segments": [seg.to_dict() for seg in all_segments]  # 返回所有線段用於繪圖
    })


# ==================== 牆類型 API ====================

@app.route('/api/projects/<int:project_id>/categories', methods=['GET'])
def get_categories(project_id):
    """取得專案的牆類型"""
    categories = db.get_categories(project_id)
    return jsonify({"success": True, "data": categories})


@app.route('/api/projects/<int:project_id>/categories', methods=['POST'])
def add_category(project_id):
    """新增牆類型"""
    data = request.json
    category_id = db.add_wall_category(
        project_id=project_id,
        code=data.get('code'),
        name=data.get('name'),
        height_type=data.get('height_type'),
        height_formula=data.get('height_formula'),
        color=data.get('color', '#888888'),
        line_weight=data.get('line_weight', 1.0)
    )
    return jsonify({"success": True, "category_id": category_id})


@app.route('/api/categories/<int:category_id>', methods=['PUT'])
def update_category(category_id):
    """更新牆類型"""
    data = request.json
    success = db.update_category(category_id, **data)
    return jsonify({"success": success})


# ==================== 結構物/棟別 API ====================

@app.route('/api/projects/<int:project_id>/buildings', methods=['GET'])
def get_buildings(project_id):
    """取得專案的所有結構物/棟別"""
    buildings = db.get_buildings(project_id)
    return jsonify({"success": True, "data": buildings})


@app.route('/api/projects/<int:project_id>/buildings', methods=['POST'])
def add_building(project_id):
    """新增結構物/棟別"""
    data = request.json
    building_id = db.add_building(
        project_id=project_id,
        code=data.get('code'),
        name=data.get('name'),
        is_basement=data.get('is_basement', False),
        display_order=data.get('display_order', 0)
    )
    return jsonify({"success": True, "building_id": building_id})


@app.route('/api/buildings/<int:building_id>', methods=['PUT'])
def update_building(building_id):
    """更新結構物/棟別"""
    data = request.json
    success = db.update_building(building_id, **data)
    return jsonify({"success": success})


# ==================== 樓層 API ====================

@app.route('/api/buildings/<int:building_id>/floors', methods=['GET'])
def get_floors(building_id):
    """取得棟別的所有樓層"""
    floors = db.get_floors(building_id)
    return jsonify({"success": True, "data": floors})


@app.route('/api/projects/<int:project_id>/floors', methods=['GET'])
def get_all_floors(project_id):
    """取得專案的所有樓層（含棟別資訊）"""
    floors = db.get_all_floors_by_project(project_id)
    return jsonify({"success": True, "data": floors})


@app.route('/api/buildings/<int:building_id>/floors', methods=['POST'])
def add_floor(building_id):
    """新增樓層"""
    data = request.json
    floor_id = db.add_floor(
        building_id=building_id,
        code=data.get('code'),
        name=data.get('name'),
        floor_level=data.get('floor_level'),
        is_combined=data.get('is_combined', False),
        display_order=data.get('display_order', 0)
    )
    return jsonify({"success": True, "floor_id": floor_id})


@app.route('/api/floors/<int:floor_id>', methods=['PUT'])
def update_floor(floor_id):
    """更新樓層"""
    data = request.json
    success = db.update_floor(floor_id, **data)
    return jsonify({"success": success})


# ==================== 圖層對應 API ====================

@app.route('/api/projects/<int:project_id>/mappings', methods=['GET'])
def get_mappings(project_id):
    """取得圖層對應"""
    mappings = db.get_layer_mappings(project_id)
    return jsonify({"success": True, "data": mappings})


@app.route('/api/projects/<int:project_id>/mappings', methods=['POST'])
def set_mapping(project_id):
    """設定圖層對應"""
    data = request.json
    db.set_layer_mapping(
        project_id=project_id,
        dxf_layer=data.get('dxf_layer'),
        category_id=data.get('category_id')
    )
    return jsonify({"success": True})


# ==================== 線段 API ====================

@app.route('/api/projects/<int:project_id>/segments', methods=['GET'])
def get_segments(project_id):
    """取得線段資料"""
    category_id = request.args.get('category_id', type=int)
    segments = db.get_segments(project_id, category_id)
    return jsonify({"success": True, "data": segments})


@app.route('/api/segments/<int:segment_id>/category', methods=['PUT'])
def update_segment_category(segment_id):
    """更新線段分類"""
    data = request.json
    success = db.update_segment_category(
        segment_id=segment_id,
        category_id=data.get('category_id')
    )
    return jsonify({"success": success})


# ==================== 統計 API ====================

@app.route('/api/projects/<int:project_id>/summary', methods=['GET'])
def get_summary(project_id):
    """取得統計摘要"""
    summary = db.get_summary(project_id)
    uncategorized = db.get_uncategorized_summary(project_id)
    
    # 計算總長度
    total_length = sum(row['total_length'] for row in summary)
    total_count = sum(row['segment_count'] for row in summary)
    
    return jsonify({
        "success": True,
        "data": {
            "by_category": summary,
            "uncategorized": uncategorized,
            "total_length": total_length,
            "total_count": total_count
        }
    })


@app.route('/api/floors/<int:floor_id>/summary', methods=['GET'])
def get_floor_summary(floor_id):
    """取得指定樓層的統計摘要"""
    # Get project_id from floor
    cursor = db.conn.cursor()
    cursor.execute("""
        SELECT b.project_id
        FROM floors f
        JOIN buildings b ON f.building_id = b.id
        WHERE f.id = ?
    """, (floor_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"success": False, "error": "樓層不存在"}), 404

    project_id = row[0]
    summary = db.get_summary_by_floor(project_id, floor_id)

    return jsonify({
        "success": True,
        "data": {
            "by_category": summary
        }
    })


@app.route('/api/buildings/<int:building_id>/summary', methods=['GET'])
def get_building_summary(building_id):
    """取得指定棟別的統計摘要（所有樓層合計）"""
    # Get project_id from building
    cursor = db.conn.cursor()
    cursor.execute("SELECT project_id FROM buildings WHERE id = ?", (building_id,))
    row = cursor.fetchone()
    if not row:
        return jsonify({"success": False, "error": "棟別不存在"}), 404

    project_id = row[0]
    summary = db.get_summary_by_building(project_id, building_id)

    return jsonify({
        "success": True,
        "data": {
            "by_category": summary
        }
    })


@app.route('/api/projects/<int:project_id>/hierarchy-summary', methods=['GET'])
def get_hierarchy_summary(project_id):
    """取得完整的分棟分樓層統計"""
    summary = db.get_full_hierarchy_summary(project_id)

    return jsonify({
        "success": True,
        "data": summary
    })


@app.route('/api/projects/<int:project_id>/export/csv', methods=['GET'])
def export_csv(project_id):
    """匯出 CSV 格式的統計表"""
    summary = db.get_summary(project_id)

    # 建立 CSV 內容
    lines = ["類型代碼,類型名稱,高度類型,高度公式,線段數,總長度(mm),總長度(m)"]
    for row in summary:
        length_m = row['total_length'] / 1000
        lines.append(f"{row['category_code']},{row['category_name']},{row['height_type']},{row['height_formula']},{row['segment_count']},{row['total_length']:.2f},{length_m:.2f}")

    csv_content = "\n".join(lines)
    
    return app.response_class(
        response=csv_content,
        status=200,
        mimetype='text/csv',
        headers={"Content-Disposition": f"attachment; filename=wall_summary_{project_id}.csv"}
    )


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Wall Quantity Calculator API Server")
    print("=" * 80)
    print("API Endpoints:")
    print("\n  專案管理:")
    print("    GET  /api/projects                          - 列出所有專案")
    print("    POST /api/projects                          - 建立新專案")
    print("    GET  /api/projects/<id>                     - 取得專案詳情")
    print("\n  結構物/棟別:")
    print("    GET  /api/projects/<id>/buildings           - 取得專案的所有棟別")
    print("    POST /api/projects/<id>/buildings           - 新增棟別")
    print("    PUT  /api/buildings/<id>                    - 更新棟別")
    print("\n  樓層:")
    print("    GET  /api/buildings/<id>/floors             - 取得棟別的所有樓層")
    print("    GET  /api/projects/<id>/floors              - 取得專案的所有樓層")
    print("    POST /api/buildings/<id>/floors             - 新增樓層")
    print("    PUT  /api/floors/<id>                       - 更新樓層")
    print("\n  牆類型:")
    print("    GET  /api/projects/<id>/categories          - 取得牆類型")
    print("    POST /api/projects/<id>/categories          - 新增牆類型")
    print("    PUT  /api/categories/<id>                   - 更新牆類型")
    print("\n  檔案處理:")
    print("    POST /api/upload                            - 上傳 DXF 檔案")
    print("    POST /api/parse                             - 解析 DXF 並建立專案")
    print("\n  統計查詢:")
    print("    GET  /api/projects/<id>/summary             - 取得專案統計")
    print("    GET  /api/buildings/<id>/summary            - 取得棟別統計")
    print("    GET  /api/floors/<id>/summary               - 取得樓層統計")
    print("    GET  /api/projects/<id>/hierarchy-summary   - 取得完整分棟分樓層統計")
    print("    GET  /api/projects/<id>/export/csv          - 匯出 CSV")
    print("=" * 80 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
