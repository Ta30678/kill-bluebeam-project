"""
DXF Group Codes Database
DXF 組碼資料庫

This module provides a comprehensive reference of DXF group codes used in AutoCAD DXF files.
Based on Autodesk's official DXF reference documentation.

組碼分類：
- 0-9: 字串
- 10-39: 浮點數座標（X, Y, Z）
- 40-59: 浮點數值
- 60-79: 16 位元整數
- 90-99: 32 位元整數
- 100: 子類別標記
- 102: 控制字串
- 105: 物件控制代碼
- 140-147: 浮點數純量
- 170-175: 16 位元整數
- 280-289: 8 位元整數
- 290-299: 布林值
- 300-309: 任意文字字串
- 310-319: 任意二進位區塊
- 320-329: 物件控制代碼
- 330-339: 軟性指標控制代碼
- 340-349: 硬性指標控制代碼
- 350-359: 軟性擁有者控制代碼
- 360-369: 硬性擁有者控制代碼
- 370-379: 線寬
- 380-389: 繪圖樣式名稱
- 390-399: 繪圖樣式控制代碼
- 400-409: 16 位元整數
- 410-419: 字串
- 420-429: 32 位元整數（真彩色值）
- 430-439: 字串（色彩名稱）
- 440-449: 32 位元整數（透明度值）
- 450-459: 長整數
- 460-469: 浮點數
- 470-479: 字串
- 480-481: 硬性指標控制代碼
- 999: 註解
- 1000-1009: 擴充資料字串
- 1010-1059: 擴充資料浮點數
- 1060-1070: 擴充資料整數
- 1071: 擴充資料長整數
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class GroupCodeCategory(Enum):
    """組碼類別"""
    STRING = "string"
    FLOAT = "float"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    HANDLE = "handle"
    BINARY = "binary"
    COORDINATE = "coordinate"


@dataclass
class GroupCodeInfo:
    """組碼資訊"""
    code: int
    category: GroupCodeCategory
    description_en: str
    description_zh: str
    data_type: str
    notes: str = ""


# 完整的 DXF 組碼資料庫
DXF_GROUP_CODES: Dict[int, GroupCodeInfo] = {
    # ==================== 字串組碼 (0-9) ====================
    0: GroupCodeInfo(0, GroupCodeCategory.STRING, "Entity type", "實體類型", "string",
                     "Identifies the entity type (LINE, CIRCLE, POLYLINE, etc.)"),
    1: GroupCodeInfo(1, GroupCodeCategory.STRING, "Primary text value", "主要文字值", "string",
                     "Primary text content for TEXT entities"),
    2: GroupCodeInfo(2, GroupCodeCategory.STRING, "Name", "名稱", "string",
                     "Block name, attribute tag, etc."),
    3: GroupCodeInfo(3, GroupCodeCategory.STRING, "Other text or name", "其他文字或名稱", "string"),
    4: GroupCodeInfo(4, GroupCodeCategory.STRING, "Other text or name", "其他文字或名稱", "string"),
    5: GroupCodeInfo(5, GroupCodeCategory.HANDLE, "Entity handle", "實體控制代碼", "string",
                     "Hex string (max 16 hex digits)"),
    6: GroupCodeInfo(6, GroupCodeCategory.STRING, "Linetype name", "線型名稱", "string"),
    7: GroupCodeInfo(7, GroupCodeCategory.STRING, "Text style name", "文字樣式名稱", "string"),
    8: GroupCodeInfo(8, GroupCodeCategory.STRING, "Layer name", "圖層名稱", "string",
                     "IMPORTANT: Identifies which layer the entity belongs to"),
    9: GroupCodeInfo(9, GroupCodeCategory.STRING, "Variable name", "變數名稱", "string",
                     "Used in HEADER section for system variables (e.g., $DIMSCALE)"),
    
    # ==================== 座標組碼 (10-39) ====================
    10: GroupCodeInfo(10, GroupCodeCategory.COORDINATE, "Primary X coordinate", "主要 X 座標", "float",
                      "Start point X / Center X"),
    11: GroupCodeInfo(11, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float",
                      "End point X / Second point X"),
    12: GroupCodeInfo(12, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float"),
    13: GroupCodeInfo(13, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float"),
    14: GroupCodeInfo(14, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float"),
    15: GroupCodeInfo(15, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float"),
    16: GroupCodeInfo(16, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float"),
    17: GroupCodeInfo(17, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float"),
    18: GroupCodeInfo(18, GroupCodeCategory.COORDINATE, "Other X coordinate", "其他 X 座標", "float"),
    
    20: GroupCodeInfo(20, GroupCodeCategory.COORDINATE, "Primary Y coordinate", "主要 Y 座標", "float",
                      "Start point Y / Center Y"),
    21: GroupCodeInfo(21, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float",
                      "End point Y / Second point Y"),
    22: GroupCodeInfo(22, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float"),
    23: GroupCodeInfo(23, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float"),
    24: GroupCodeInfo(24, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float"),
    25: GroupCodeInfo(25, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float"),
    26: GroupCodeInfo(26, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float"),
    27: GroupCodeInfo(27, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float"),
    28: GroupCodeInfo(28, GroupCodeCategory.COORDINATE, "Other Y coordinate", "其他 Y 座標", "float"),
    
    30: GroupCodeInfo(30, GroupCodeCategory.COORDINATE, "Primary Z coordinate", "主要 Z 座標", "float",
                      "Start point Z / Center Z"),
    31: GroupCodeInfo(31, GroupCodeCategory.COORDINATE, "Other Z coordinate", "其他 Z 座標", "float",
                      "End point Z / Second point Z"),
    32: GroupCodeInfo(32, GroupCodeCategory.COORDINATE, "Other Z coordinate", "其他 Z 座標", "float"),
    33: GroupCodeInfo(33, GroupCodeCategory.COORDINATE, "Other Z coordinate", "其他 Z 座標", "float"),
    34: GroupCodeInfo(34, GroupCodeCategory.COORDINATE, "Other Z coordinate", "其他 Z 座標", "float"),
    35: GroupCodeInfo(35, GroupCodeCategory.COORDINATE, "Other Z coordinate", "其他 Z 座標", "float"),
    36: GroupCodeInfo(36, GroupCodeCategory.COORDINATE, "Other Z coordinate", "其他 Z 座標", "float"),
    37: GroupCodeInfo(37, GroupCodeCategory.COORDINATE, "Other Z coordinate", "其他 Z 座標", "float"),
    38: GroupCodeInfo(38, GroupCodeCategory.FLOAT, "Elevation", "高程", "float"),
    39: GroupCodeInfo(39, GroupCodeCategory.FLOAT, "Thickness", "厚度", "float"),
    
    # ==================== 浮點數值組碼 (40-59) ====================
    40: GroupCodeInfo(40, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float",
                      "Radius, ratio, scale factor, etc."),
    41: GroupCodeInfo(41, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float",
                      "Width, X scale factor, etc."),
    42: GroupCodeInfo(42, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float",
                      "Bulge, Y scale factor, etc."),
    43: GroupCodeInfo(43, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    44: GroupCodeInfo(44, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    45: GroupCodeInfo(45, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    46: GroupCodeInfo(46, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    47: GroupCodeInfo(47, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    48: GroupCodeInfo(48, GroupCodeCategory.FLOAT, "Linetype scale", "線型比例", "float"),
    49: GroupCodeInfo(49, GroupCodeCategory.FLOAT, "Repeated float value", "重複浮點值", "float"),
    
    50: GroupCodeInfo(50, GroupCodeCategory.FLOAT, "Angle", "角度", "float",
                      "Angle in degrees (start angle, rotation, etc.)"),
    51: GroupCodeInfo(51, GroupCodeCategory.FLOAT, "Angle", "角度", "float",
                      "End angle, other angles"),
    52: GroupCodeInfo(52, GroupCodeCategory.FLOAT, "Angle", "角度", "float"),
    53: GroupCodeInfo(53, GroupCodeCategory.FLOAT, "Angle", "角度", "float"),
    54: GroupCodeInfo(54, GroupCodeCategory.FLOAT, "Angle", "角度", "float"),
    55: GroupCodeInfo(55, GroupCodeCategory.FLOAT, "Angle", "角度", "float"),
    
    # ==================== 16 位元整數組碼 (60-79) ====================
    60: GroupCodeInfo(60, GroupCodeCategory.INTEGER, "Entity visibility", "實體可見性", "int16",
                      "0 = Visible, 1 = Invisible"),
    62: GroupCodeInfo(62, GroupCodeCategory.INTEGER, "Color number", "顏色編號", "int16",
                      "AutoCAD Color Index (ACI), 0 = ByBlock, 256 = ByLayer"),
    66: GroupCodeInfo(66, GroupCodeCategory.INTEGER, "Entities follow flag", "後續實體標記", "int16"),
    67: GroupCodeInfo(67, GroupCodeCategory.INTEGER, "Model/Paper space", "模型/圖紙空間", "int16",
                      "0 = Model space, 1 = Paper space"),
    68: GroupCodeInfo(68, GroupCodeCategory.INTEGER, "Viewport status", "視埠狀態", "int16"),
    69: GroupCodeInfo(69, GroupCodeCategory.INTEGER, "Viewport identification", "視埠識別", "int16"),
    
    70: GroupCodeInfo(70, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16",
                      "Flags, counts, modes"),
    71: GroupCodeInfo(71, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    72: GroupCodeInfo(72, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    73: GroupCodeInfo(73, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    74: GroupCodeInfo(74, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    75: GroupCodeInfo(75, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    76: GroupCodeInfo(76, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    77: GroupCodeInfo(77, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    78: GroupCodeInfo(78, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    79: GroupCodeInfo(79, GroupCodeCategory.INTEGER, "Integer value", "整數值", "int16"),
    
    # ==================== 32 位元整數組碼 (90-99) ====================
    90: GroupCodeInfo(90, GroupCodeCategory.INTEGER, "32-bit integer", "32 位元整數", "int32"),
    91: GroupCodeInfo(91, GroupCodeCategory.INTEGER, "32-bit integer", "32 位元整數", "int32"),
    92: GroupCodeInfo(92, GroupCodeCategory.INTEGER, "32-bit integer", "32 位元整數", "int32"),
    93: GroupCodeInfo(93, GroupCodeCategory.INTEGER, "32-bit integer", "32 位元整數", "int32"),
    94: GroupCodeInfo(94, GroupCodeCategory.INTEGER, "32-bit integer", "32 位元整數", "int32"),
    95: GroupCodeInfo(95, GroupCodeCategory.INTEGER, "32-bit integer", "32 位元整數", "int32"),
    
    # ==================== 特殊組碼 (100-105) ====================
    100: GroupCodeInfo(100, GroupCodeCategory.STRING, "Subclass marker", "子類別標記", "string",
                       "Indicates the class data that follows (e.g., AcDbEntity, AcDbLine)"),
    102: GroupCodeInfo(102, GroupCodeCategory.STRING, "Control string", "控制字串", "string",
                       "Starts with '{' or ends with '}'"),
    105: GroupCodeInfo(105, GroupCodeCategory.HANDLE, "DIMVAR symbol table handle", "標注變數符號表控制代碼", "handle"),
    
    # ==================== 浮點數組碼 (140-149) ====================
    140: GroupCodeInfo(140, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    141: GroupCodeInfo(141, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    142: GroupCodeInfo(142, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    143: GroupCodeInfo(143, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    144: GroupCodeInfo(144, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    145: GroupCodeInfo(145, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    146: GroupCodeInfo(146, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    147: GroupCodeInfo(147, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    148: GroupCodeInfo(148, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    149: GroupCodeInfo(149, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    
    # ==================== 16 位元整數組碼 (170-179) ====================
    170: GroupCodeInfo(170, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    171: GroupCodeInfo(171, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    172: GroupCodeInfo(172, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    173: GroupCodeInfo(173, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    174: GroupCodeInfo(174, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    175: GroupCodeInfo(175, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    176: GroupCodeInfo(176, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    177: GroupCodeInfo(177, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    178: GroupCodeInfo(178, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    179: GroupCodeInfo(179, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    
    # ==================== 擴充資料組碼 (210-239) ====================
    210: GroupCodeInfo(210, GroupCodeCategory.COORDINATE, "Extrusion direction X", "擠出方向 X", "float"),
    220: GroupCodeInfo(220, GroupCodeCategory.COORDINATE, "Extrusion direction Y", "擠出方向 Y", "float"),
    230: GroupCodeInfo(230, GroupCodeCategory.COORDINATE, "Extrusion direction Z", "擠出方向 Z", "float"),
    
    # ==================== 8 位元整數組碼 (280-289) ====================
    280: GroupCodeInfo(280, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    281: GroupCodeInfo(281, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    282: GroupCodeInfo(282, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    283: GroupCodeInfo(283, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    284: GroupCodeInfo(284, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    285: GroupCodeInfo(285, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    286: GroupCodeInfo(286, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    287: GroupCodeInfo(287, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    288: GroupCodeInfo(288, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    289: GroupCodeInfo(289, GroupCodeCategory.INTEGER, "8-bit integer", "8 位元整數", "int8"),
    
    # ==================== 布林值組碼 (290-299) ====================
    290: GroupCodeInfo(290, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    291: GroupCodeInfo(291, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    292: GroupCodeInfo(292, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    293: GroupCodeInfo(293, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    294: GroupCodeInfo(294, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    295: GroupCodeInfo(295, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    296: GroupCodeInfo(296, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    297: GroupCodeInfo(297, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    298: GroupCodeInfo(298, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    299: GroupCodeInfo(299, GroupCodeCategory.BOOLEAN, "Boolean flag", "布林標記", "bool"),
    
    # ==================== 任意字串組碼 (300-309) ====================
    300: GroupCodeInfo(300, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    301: GroupCodeInfo(301, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    302: GroupCodeInfo(302, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    303: GroupCodeInfo(303, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    304: GroupCodeInfo(304, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    305: GroupCodeInfo(305, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    306: GroupCodeInfo(306, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    307: GroupCodeInfo(307, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    308: GroupCodeInfo(308, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    309: GroupCodeInfo(309, GroupCodeCategory.STRING, "Arbitrary text string", "任意文字字串", "string"),
    
    # ==================== 二進位資料組碼 (310-319) ====================
    310: GroupCodeInfo(310, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    311: GroupCodeInfo(311, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    312: GroupCodeInfo(312, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    313: GroupCodeInfo(313, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    314: GroupCodeInfo(314, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    315: GroupCodeInfo(315, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    316: GroupCodeInfo(316, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    317: GroupCodeInfo(317, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    318: GroupCodeInfo(318, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    319: GroupCodeInfo(319, GroupCodeCategory.BINARY, "Arbitrary binary chunk", "任意二進位區塊", "binary"),
    
    # ==================== 物件控制代碼組碼 (320-339) ====================
    320: GroupCodeInfo(320, GroupCodeCategory.HANDLE, "Arbitrary object handle", "任意物件控制代碼", "handle"),
    330: GroupCodeInfo(330, GroupCodeCategory.HANDLE, "Soft-pointer handle", "軟性指標控制代碼", "handle",
                       "References to other entities (owner, dictionary, etc.)"),
    331: GroupCodeInfo(331, GroupCodeCategory.HANDLE, "Soft-pointer handle", "軟性指標控制代碼", "handle"),
    332: GroupCodeInfo(332, GroupCodeCategory.HANDLE, "Soft-pointer handle", "軟性指標控制代碼", "handle"),
    333: GroupCodeInfo(333, GroupCodeCategory.HANDLE, "Soft-pointer handle", "軟性指標控制代碼", "handle"),
    340: GroupCodeInfo(340, GroupCodeCategory.HANDLE, "Hard-pointer handle", "硬性指標控制代碼", "handle"),
    341: GroupCodeInfo(341, GroupCodeCategory.HANDLE, "Hard-pointer handle", "硬性指標控制代碼", "handle"),
    342: GroupCodeInfo(342, GroupCodeCategory.HANDLE, "Hard-pointer handle", "硬性指標控制代碼", "handle"),
    343: GroupCodeInfo(343, GroupCodeCategory.HANDLE, "Hard-pointer handle", "硬性指標控制代碼", "handle"),
    350: GroupCodeInfo(350, GroupCodeCategory.HANDLE, "Soft-owner handle", "軟性擁有者控制代碼", "handle"),
    351: GroupCodeInfo(351, GroupCodeCategory.HANDLE, "Soft-owner handle", "軟性擁有者控制代碼", "handle"),
    360: GroupCodeInfo(360, GroupCodeCategory.HANDLE, "Hard-owner handle", "硬性擁有者控制代碼", "handle"),
    361: GroupCodeInfo(361, GroupCodeCategory.HANDLE, "Hard-owner handle", "硬性擁有者控制代碼", "handle"),
    
    # ==================== 線寬組碼 (370-379) ====================
    370: GroupCodeInfo(370, GroupCodeCategory.INTEGER, "Lineweight", "線寬", "int16",
                       "Lineweight in 0.01mm units (-1=ByLayer, -2=ByBlock, -3=Default)"),
    371: GroupCodeInfo(371, GroupCodeCategory.INTEGER, "Lineweight", "線寬", "int16"),
    
    # ==================== 繪圖樣式組碼 (380-399) ====================
    380: GroupCodeInfo(380, GroupCodeCategory.STRING, "PlotStyle name type", "繪圖樣式名稱類型", "int16"),
    390: GroupCodeInfo(390, GroupCodeCategory.HANDLE, "PlotStyle handle", "繪圖樣式控制代碼", "handle"),
    
    # ==================== 16 位元整數組碼 (400-409) ====================
    400: GroupCodeInfo(400, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    401: GroupCodeInfo(401, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    402: GroupCodeInfo(402, GroupCodeCategory.INTEGER, "16-bit integer", "16 位元整數", "int16"),
    
    # ==================== 配置名稱組碼 (410-419) ====================
    410: GroupCodeInfo(410, GroupCodeCategory.STRING, "Layout name", "配置名稱", "string"),
    411: GroupCodeInfo(411, GroupCodeCategory.STRING, "String", "字串", "string"),
    
    # ==================== 真彩色組碼 (420-429) ====================
    420: GroupCodeInfo(420, GroupCodeCategory.INTEGER, "True color value", "真彩色值", "int32",
                       "24-bit RGB value (0x00RRGGBB)"),
    421: GroupCodeInfo(421, GroupCodeCategory.INTEGER, "True color value", "真彩色值", "int32"),
    422: GroupCodeInfo(422, GroupCodeCategory.INTEGER, "True color value", "真彩色值", "int32"),
    
    # ==================== 色彩名稱組碼 (430-439) ====================
    430: GroupCodeInfo(430, GroupCodeCategory.STRING, "Color name", "色彩名稱", "string"),
    431: GroupCodeInfo(431, GroupCodeCategory.STRING, "Color name", "色彩名稱", "string"),
    
    # ==================== 透明度組碼 (440-449) ====================
    440: GroupCodeInfo(440, GroupCodeCategory.INTEGER, "Transparency value", "透明度值", "int32",
                       "0x020000FF = fully opaque"),
    
    # ==================== 漸層填充組碼 (450-469) ====================
    450: GroupCodeInfo(450, GroupCodeCategory.INTEGER, "Long integer", "長整數", "int32"),
    451: GroupCodeInfo(451, GroupCodeCategory.INTEGER, "Long integer", "長整數", "int32"),
    452: GroupCodeInfo(452, GroupCodeCategory.INTEGER, "Long integer", "長整數", "int32"),
    453: GroupCodeInfo(453, GroupCodeCategory.INTEGER, "Long integer", "長整數", "int32"),
    460: GroupCodeInfo(460, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    461: GroupCodeInfo(461, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    462: GroupCodeInfo(462, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    463: GroupCodeInfo(463, GroupCodeCategory.FLOAT, "Float value", "浮點數值", "float"),
    
    # ==================== 字串組碼 (470-479) ====================
    470: GroupCodeInfo(470, GroupCodeCategory.STRING, "String", "字串", "string"),
    471: GroupCodeInfo(471, GroupCodeCategory.STRING, "String", "字串", "string"),
    
    # ==================== 硬性指標組碼 (480-481) ====================
    480: GroupCodeInfo(480, GroupCodeCategory.HANDLE, "Hard-pointer handle", "硬性指標控制代碼", "handle"),
    481: GroupCodeInfo(481, GroupCodeCategory.HANDLE, "Hard-pointer handle", "硬性指標控制代碼", "handle"),
    
    # ==================== 註解組碼 (999) ====================
    999: GroupCodeInfo(999, GroupCodeCategory.STRING, "Comment", "註解", "string",
                       "Comments added by AutoCAD or third-party applications"),
    
    # ==================== 擴充資料組碼 (1000-1071) ====================
    1000: GroupCodeInfo(1000, GroupCodeCategory.STRING, "Extended data string", "擴充資料字串", "string"),
    1001: GroupCodeInfo(1001, GroupCodeCategory.STRING, "Extended data application name", "擴充資料應用程式名稱", "string"),
    1002: GroupCodeInfo(1002, GroupCodeCategory.STRING, "Extended data control string", "擴充資料控制字串", "string"),
    1003: GroupCodeInfo(1003, GroupCodeCategory.STRING, "Extended data layer name", "擴充資料圖層名稱", "string"),
    1004: GroupCodeInfo(1004, GroupCodeCategory.BINARY, "Extended data binary data", "擴充資料二進位資料", "binary"),
    1005: GroupCodeInfo(1005, GroupCodeCategory.HANDLE, "Extended data handle", "擴充資料控制代碼", "handle"),
    
    1010: GroupCodeInfo(1010, GroupCodeCategory.COORDINATE, "Extended data X coordinate", "擴充資料 X 座標", "float"),
    1011: GroupCodeInfo(1011, GroupCodeCategory.COORDINATE, "Extended data 3D world space X", "擴充資料 3D 世界空間 X", "float"),
    1012: GroupCodeInfo(1012, GroupCodeCategory.COORDINATE, "Extended data displacement X", "擴充資料位移 X", "float"),
    1013: GroupCodeInfo(1013, GroupCodeCategory.COORDINATE, "Extended data direction X", "擴充資料方向 X", "float"),
    
    1020: GroupCodeInfo(1020, GroupCodeCategory.COORDINATE, "Extended data Y coordinate", "擴充資料 Y 座標", "float"),
    1021: GroupCodeInfo(1021, GroupCodeCategory.COORDINATE, "Extended data 3D world space Y", "擴充資料 3D 世界空間 Y", "float"),
    1022: GroupCodeInfo(1022, GroupCodeCategory.COORDINATE, "Extended data displacement Y", "擴充資料位移 Y", "float"),
    1023: GroupCodeInfo(1023, GroupCodeCategory.COORDINATE, "Extended data direction Y", "擴充資料方向 Y", "float"),
    
    1030: GroupCodeInfo(1030, GroupCodeCategory.COORDINATE, "Extended data Z coordinate", "擴充資料 Z 座標", "float"),
    1031: GroupCodeInfo(1031, GroupCodeCategory.COORDINATE, "Extended data 3D world space Z", "擴充資料 3D 世界空間 Z", "float"),
    1032: GroupCodeInfo(1032, GroupCodeCategory.COORDINATE, "Extended data displacement Z", "擴充資料位移 Z", "float"),
    1033: GroupCodeInfo(1033, GroupCodeCategory.COORDINATE, "Extended data direction Z", "擴充資料方向 Z", "float"),
    
    1040: GroupCodeInfo(1040, GroupCodeCategory.FLOAT, "Extended data float", "擴充資料浮點數", "float"),
    1041: GroupCodeInfo(1041, GroupCodeCategory.FLOAT, "Extended data distance", "擴充資料距離", "float"),
    1042: GroupCodeInfo(1042, GroupCodeCategory.FLOAT, "Extended data scale factor", "擴充資料比例因子", "float"),
    
    1060: GroupCodeInfo(1060, GroupCodeCategory.INTEGER, "Extended data 16-bit integer", "擴充資料 16 位元整數", "int16"),
    1061: GroupCodeInfo(1061, GroupCodeCategory.INTEGER, "Extended data 16-bit unsigned", "擴充資料 16 位元無符號整數", "uint16"),
    1070: GroupCodeInfo(1070, GroupCodeCategory.INTEGER, "Extended data 16-bit integer", "擴充資料 16 位元整數", "int16"),
    1071: GroupCodeInfo(1071, GroupCodeCategory.INTEGER, "Extended data 32-bit integer", "擴充資料 32 位元整數", "int32"),
}


# ==================== DXF 標頭變數資料庫 ====================
DXF_HEADER_VARIABLES: Dict[str, Dict[str, Any]] = {
    # ==================== 尺寸相關變數 ====================
    "$DIMSCALE": {
        "group_code": 40,
        "type": "float",
        "default": 1.0,
        "description_en": "Overall dimensioning scale factor",
        "description_zh": "整體標注比例因子",
        "notes": "CRITICAL: This affects how dimensions are scaled. For 1:100 drawings, DIMSCALE = 100"
    },
    "$DIMLFAC": {
        "group_code": 40,
        "type": "float", 
        "default": 1.0,
        "description_en": "Linear dimension scale factor",
        "description_zh": "線性標注比例因子",
        "notes": "Multiplier for linear dimension measurements"
    },
    "$DIMTXT": {
        "group_code": 40,
        "type": "float",
        "default": 0.18,
        "description_en": "Dimension text height",
        "description_zh": "標注文字高度"
    },
    "$DIMASZ": {
        "group_code": 40,
        "type": "float",
        "default": 0.18,
        "description_en": "Dimension arrow size",
        "description_zh": "標注箭頭大小"
    },
    
    # ==================== 單位相關變數 ====================
    "$INSUNITS": {
        "group_code": 70,
        "type": "int16",
        "default": 0,
        "description_en": "Drawing units for automatic scaling of inserted content",
        "description_zh": "插入內容自動縮放的繪圖單位",
        "values": {
            0: "Unspecified (無指定)",
            1: "Inches (英寸)",
            2: "Feet (英尺)",
            3: "Miles (英里)",
            4: "Millimeters (毫米)",
            5: "Centimeters (公分)",
            6: "Meters (公尺)",
            7: "Kilometers (公里)",
            8: "Microinches (微英寸)",
            9: "Mils (密爾)",
            10: "Yards (碼)",
            11: "Angstroms (埃)",
            12: "Nanometers (奈米)",
            13: "Microns (微米)",
            14: "Decimeters (分米)",
            15: "Decameters (十公尺)",
            16: "Hectometers (百公尺)",
            17: "Gigameters (十億公尺)",
            18: "Astronomical units (天文單位)",
            19: "Light years (光年)",
            20: "Parsecs (秒差距)"
        }
    },
    "$LUNITS": {
        "group_code": 70,
        "type": "int16",
        "default": 2,
        "description_en": "Linear units format",
        "description_zh": "線性單位格式",
        "values": {
            1: "Scientific (科學記號)",
            2: "Decimal (十進位)",
            3: "Engineering (工程)",
            4: "Architectural (建築)",
            5: "Fractional (分數)"
        }
    },
    "$LUPREC": {
        "group_code": 70,
        "type": "int16",
        "default": 4,
        "description_en": "Linear units decimal places",
        "description_zh": "線性單位小數位數"
    },
    "$AUNITS": {
        "group_code": 70,
        "type": "int16",
        "default": 0,
        "description_en": "Angular units format",
        "description_zh": "角度單位格式",
        "values": {
            0: "Decimal degrees (十進位角度)",
            1: "Degrees/minutes/seconds (度分秒)",
            2: "Gradians (百分度)",
            3: "Radians (弧度)",
            4: "Surveyor's units (測量單位)"
        }
    },
    
    # ==================== 繪圖範圍變數 ====================
    "$EXTMIN": {
        "group_code": [10, 20, 30],
        "type": "point",
        "description_en": "Drawing extents minimum point",
        "description_zh": "繪圖範圍最小點"
    },
    "$EXTMAX": {
        "group_code": [10, 20, 30],
        "type": "point",
        "description_en": "Drawing extents maximum point",
        "description_zh": "繪圖範圍最大點"
    },
    "$LIMMIN": {
        "group_code": [10, 20],
        "type": "point2d",
        "description_en": "Drawing limits minimum point",
        "description_zh": "繪圖界限最小點"
    },
    "$LIMMAX": {
        "group_code": [10, 20],
        "type": "point2d",
        "description_en": "Drawing limits maximum point",
        "description_zh": "繪圖界限最大點"
    },
    
    # ==================== 版本相關變數 ====================
    "$ACADVER": {
        "group_code": 1,
        "type": "string",
        "description_en": "AutoCAD version number",
        "description_zh": "AutoCAD 版本號"
    },
    "$DWGCODEPAGE": {
        "group_code": 3,
        "type": "string",
        "description_en": "Drawing code page",
        "description_zh": "繪圖代碼頁",
        "notes": "Character encoding used in the drawing"
    },
    
    # ==================== 圖層相關變數 ====================
    "$CLAYER": {
        "group_code": 8,
        "type": "string",
        "default": "0",
        "description_en": "Current layer name",
        "description_zh": "目前圖層名稱"
    },
    "$CECOLOR": {
        "group_code": 62,
        "type": "int16",
        "default": 256,
        "description_en": "Current entity color number",
        "description_zh": "目前實體顏色編號",
        "notes": "0 = ByBlock, 256 = ByLayer"
    },
    "$CELTYPE": {
        "group_code": 6,
        "type": "string",
        "default": "BYLAYER",
        "description_en": "Current entity linetype name",
        "description_zh": "目前實體線型名稱"
    },
    "$CELTSCALE": {
        "group_code": 40,
        "type": "float",
        "default": 1.0,
        "description_en": "Current entity linetype scale",
        "description_zh": "目前實體線型比例"
    },
    
    # ==================== 繪圖設定變數 ====================
    "$LTSCALE": {
        "group_code": 40,
        "type": "float",
        "default": 1.0,
        "description_en": "Global linetype scale",
        "description_zh": "整體線型比例"
    },
    "$PDSIZE": {
        "group_code": 40,
        "type": "float",
        "default": 0.0,
        "description_en": "Point display size",
        "description_zh": "點顯示大小"
    },
    "$PDMODE": {
        "group_code": 70,
        "type": "int16",
        "default": 0,
        "description_en": "Point display mode",
        "description_zh": "點顯示模式"
    },
}


# ==================== DXF 實體類型資料庫 ====================
DXF_ENTITY_TYPES: Dict[str, Dict[str, Any]] = {
    "LINE": {
        "description_en": "Line entity",
        "description_zh": "直線實體",
        "common_codes": {
            10: "Start point X",
            20: "Start point Y", 
            30: "Start point Z",
            11: "End point X",
            21: "End point Y",
            31: "End point Z"
        },
        "calculation": "length = sqrt((x2-x1)^2 + (y2-y1)^2 + (z2-z1)^2)"
    },
    "LWPOLYLINE": {
        "description_en": "Lightweight polyline entity",
        "description_zh": "輕量多段線實體",
        "common_codes": {
            10: "Vertex X",
            20: "Vertex Y",
            40: "Start width",
            41: "End width",
            42: "Bulge",
            70: "Polyline flag (1=closed)",
            90: "Number of vertices"
        },
        "calculation": "Sum of segment lengths between consecutive vertices"
    },
    "POLYLINE": {
        "description_en": "Polyline entity (old style)",
        "description_zh": "多段線實體（舊版）",
        "common_codes": {
            66: "Vertices follow flag",
            70: "Polyline flags"
        }
    },
    "CIRCLE": {
        "description_en": "Circle entity",
        "description_zh": "圓形實體",
        "common_codes": {
            10: "Center X",
            20: "Center Y",
            30: "Center Z",
            40: "Radius"
        },
        "calculation": "circumference = 2 * PI * radius"
    },
    "ARC": {
        "description_en": "Arc entity",
        "description_zh": "弧線實體",
        "common_codes": {
            10: "Center X",
            20: "Center Y",
            30: "Center Z",
            40: "Radius",
            50: "Start angle (degrees)",
            51: "End angle (degrees)"
        },
        "calculation": "arc_length = radius * (end_angle - start_angle) in radians"
    },
    "ELLIPSE": {
        "description_en": "Ellipse entity",
        "description_zh": "橢圓實體",
        "common_codes": {
            10: "Center X",
            20: "Center Y",
            30: "Center Z",
            11: "Major axis endpoint X (relative to center)",
            21: "Major axis endpoint Y",
            31: "Major axis endpoint Z",
            40: "Ratio of minor axis to major axis",
            41: "Start parameter",
            42: "End parameter"
        }
    },
    "SPLINE": {
        "description_en": "Spline entity",
        "description_zh": "樣條曲線實體",
        "common_codes": {
            70: "Spline flag",
            71: "Degree of spline",
            72: "Number of knots",
            73: "Number of control points",
            74: "Number of fit points",
            10: "Control point X",
            20: "Control point Y",
            30: "Control point Z"
        }
    },
    "TEXT": {
        "description_en": "Single-line text entity",
        "description_zh": "單行文字實體",
        "common_codes": {
            1: "Text content",
            10: "First alignment point X",
            20: "First alignment point Y",
            30: "First alignment point Z",
            40: "Text height",
            50: "Rotation angle",
            7: "Text style name",
            72: "Horizontal text justification",
            73: "Vertical text justification"
        }
    },
    "MTEXT": {
        "description_en": "Multi-line text entity",
        "description_zh": "多行文字實體",
        "common_codes": {
            1: "Text content",
            3: "Additional text content",
            10: "Insertion point X",
            20: "Insertion point Y",
            30: "Insertion point Z",
            40: "Nominal text height",
            41: "Reference rectangle width",
            50: "Rotation angle",
            71: "Attachment point"
        }
    },
    "INSERT": {
        "description_en": "Block reference entity",
        "description_zh": "圖塊參考實體",
        "common_codes": {
            2: "Block name",
            10: "Insertion point X",
            20: "Insertion point Y",
            30: "Insertion point Z",
            41: "X scale factor",
            42: "Y scale factor",
            43: "Z scale factor",
            50: "Rotation angle",
            66: "Attributes follow flag"
        }
    },
    "DIMENSION": {
        "description_en": "Dimension entity",
        "description_zh": "標注實體",
        "common_codes": {
            2: "Name of block containing dimension graphics",
            10: "Definition point X",
            20: "Definition point Y",
            30: "Definition point Z",
            11: "Middle point of dimension text X",
            21: "Middle point of dimension text Y",
            31: "Middle point of dimension text Z",
            70: "Dimension type",
            1: "Dimension text override"
        }
    },
    "HATCH": {
        "description_en": "Hatch entity",
        "description_zh": "填充實體",
        "common_codes": {
            2: "Hatch pattern name",
            70: "Solid fill flag",
            71: "Associativity flag",
            91: "Number of boundary paths",
            41: "Hatch pattern scale",
            52: "Hatch pattern angle"
        }
    },
    "SOLID": {
        "description_en": "2D solid filled polygon",
        "description_zh": "2D 實心填充多邊形",
        "common_codes": {
            10: "First corner X",
            20: "First corner Y",
            11: "Second corner X",
            21: "Second corner Y",
            12: "Third corner X",
            22: "Third corner Y",
            13: "Fourth corner X",
            23: "Fourth corner Y"
        }
    },
    "POINT": {
        "description_en": "Point entity",
        "description_zh": "點實體",
        "common_codes": {
            10: "Point X",
            20: "Point Y",
            30: "Point Z"
        }
    },
    "3DFACE": {
        "description_en": "3D face entity",
        "description_zh": "3D 面實體",
        "common_codes": {
            10: "First corner X",
            20: "First corner Y",
            30: "First corner Z",
            11: "Second corner X",
            21: "Second corner Y",
            31: "Second corner Z",
            12: "Third corner X",
            22: "Third corner Y",
            32: "Third corner Z",
            13: "Fourth corner X",
            23: "Fourth corner Y",
            33: "Fourth corner Z"
        }
    },
    "VIEWPORT": {
        "description_en": "Viewport entity",
        "description_zh": "視埠實體",
        "common_codes": {
            10: "Center point X",
            20: "Center point Y",
            40: "Width in paper space units",
            41: "Height in paper space units",
            68: "Viewport status field",
            69: "Viewport ID"
        }
    }
}


# ==================== 輔助函數 ====================

def get_group_code_info(code: int) -> Optional[GroupCodeInfo]:
    """取得組碼資訊"""
    return DXF_GROUP_CODES.get(code)


def get_group_code_category(code: int) -> Optional[GroupCodeCategory]:
    """取得組碼類別"""
    info = get_group_code_info(code)
    return info.category if info else None


def get_header_variable_info(var_name: str) -> Optional[Dict[str, Any]]:
    """取得標頭變數資訊"""
    return DXF_HEADER_VARIABLES.get(var_name)


def get_entity_type_info(entity_type: str) -> Optional[Dict[str, Any]]:
    """取得實體類型資訊"""
    return DXF_ENTITY_TYPES.get(entity_type.upper())


def interpret_group_code(code: int, value: Any, context: str = "entity") -> Dict[str, Any]:
    """
    解釋組碼及其值
    
    Args:
        code: 組碼
        value: 組碼對應的值
        context: 上下文 ("entity", "header", "table")
    
    Returns:
        包含解釋資訊的字典
    """
    info = get_group_code_info(code)
    
    result = {
        "code": code,
        "value": value,
        "description_en": info.description_en if info else "Unknown",
        "description_zh": info.description_zh if info else "未知",
        "category": info.category.value if info else "unknown",
        "data_type": info.data_type if info else "unknown"
    }
    
    # 特殊處理某些組碼
    if code == 62:  # 顏色
        if value == 0:
            result["interpreted"] = "ByBlock (依圖塊)"
        elif value == 256:
            result["interpreted"] = "ByLayer (依圖層)"
        elif value < 0:
            result["interpreted"] = f"Layer off color: {abs(value)}"
        else:
            result["interpreted"] = f"ACI Color #{value}"
    
    elif code == 70:  # 整數標記
        result["interpreted"] = f"Flag/Count: {value}"
    
    elif code == 8:  # 圖層名稱
        result["interpreted"] = f"Layer: {value}"
    
    elif code in [10, 20, 30]:  # 座標
        coord = {10: "X", 20: "Y", 30: "Z"}
        result["interpreted"] = f"{coord[code]} coordinate: {value}"
    
    return result


def get_units_conversion_factor(insunits: int, target_unit: str = "mm") -> float:
    """
    取得單位轉換係數
    
    Args:
        insunits: INSUNITS 變數值
        target_unit: 目標單位 ("mm", "m", "inch", "feet")
    
    Returns:
        轉換係數（乘以此值可將繪圖單位轉換為目標單位）
    """
    # 先轉換為毫米
    to_mm = {
        0: 1.0,      # 無指定，假設是毫米
        1: 25.4,     # 英寸
        2: 304.8,    # 英尺
        3: 1609344.0,  # 英里
        4: 1.0,      # 毫米
        5: 10.0,     # 公分
        6: 1000.0,   # 公尺
        7: 1000000.0,  # 公里
        8: 0.0000254,  # 微英寸
        9: 0.0254,   # 密爾
        10: 914.4,   # 碼
        11: 0.0000001,  # 埃
        12: 0.000001,  # 奈米
        13: 0.001,   # 微米
        14: 100.0,   # 分米
        15: 10000.0,  # 十公尺
        16: 100000.0,  # 百公尺
    }
    
    mm_factor = to_mm.get(insunits, 1.0)
    
    # 從毫米轉換到目標單位
    from_mm = {
        "mm": 1.0,
        "m": 0.001,
        "cm": 0.1,
        "inch": 1 / 25.4,
        "feet": 1 / 304.8,
    }
    
    return mm_factor * from_mm.get(target_unit, 1.0)


# ==================== 測試 ====================
if __name__ == "__main__":
    # 測試組碼查詢
    print("=== DXF Group Codes Database Test ===\n")
    
    test_codes = [0, 8, 10, 20, 40, 62, 100]
    for code in test_codes:
        info = get_group_code_info(code)
        if info:
            print(f"Code {code}: {info.description_zh} ({info.data_type})")
    
    print("\n=== Header Variables Test ===\n")
    
    test_vars = ["$DIMSCALE", "$INSUNITS", "$CLAYER"]
    for var in test_vars:
        info = get_header_variable_info(var)
        if info:
            print(f"{var}: {info['description_zh']}")
    
    print("\n=== Entity Types Test ===\n")
    
    test_entities = ["LINE", "CIRCLE", "LWPOLYLINE"]
    for entity in test_entities:
        info = get_entity_type_info(entity)
        if info:
            print(f"{entity}: {info['description_zh']}")
