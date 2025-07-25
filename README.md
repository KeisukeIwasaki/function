# AreaPersonCounter

**AreaPersonCounter** は、画像内で検出された人物のバウンディングボックス情報をもとに、事前に定義したエリアごとに人物を分類・カウント・可視化・レポート出力する Python スクリプトです。

---

## 📌 主な機能

* 多角形で定義されたエリアへの人物の分類
* 各エリアごとの人数カウント
* 可視化（エリアと人物位置）
* 詳細レポートの生成（信頼度・座標・識別番号付き）

---

## 💡 使用例

```python
from area_person_counter import AreaPersonCounter

# バウンディングボックス例
sample_bboxes = [
    {"x1": 100, "y1": 200, "x2": 150, "y2": 350, "confidence": 0.9},
    {"x1": 300, "y1": 250, "x2": 360, "y2": 400, "confidence": 0.8},
    ...
]

counter = AreaPersonCounter(image_width=1024, image_height=576)

# 人数をカウント
result = counter.count_people_by_area(sample_bboxes)

# レポートを出力
print(counter.generate_report(sample_bboxes))

# 可視化（表示または保存）
counter.visualize_areas_and_detections(sample_bboxes, save_path="result.png")
```

---

## 🛠️ セットアップ

### 必要なライブラリ

```bash
pip install matplotlib numpy
```

---

## 🧱️ クラス構成

### `AreaPersonCounter`

| メソッド名                                                    | 説明                       |
| -------------------------------------------------------- | ------------------------ |
| `count_people_by_area(bboxes)`                           | バウンディングボックスをエリア分類してカウント  |
| `classify_person_to_area(bbox)`                          | 足元の座標により人物をエリアに分類        |
| `visualize_areas_and_detections(bboxes, save_path=None)` | エリアと人物位置をプロット表示（画像保存も可能） |
| `generate_report(bboxes)`                                | エリア別人数・詳細付きのレポートを生成      |
| `get_bbox_bottom_center(bbox)`                           | バウンディングボックス底辺の中心座標を取得    |
| `point_in_polygon(point, polygon)`                       | レイキャスティング法で点の多角形内判定      |

---

## 📊 出力例

```
==================================================
エリア別人数カウント結果
==================================================
総検出数: 15人

【エリア別集計】
エリアB: 0人
エリアC: 9人
エリアA: 0人
エリアD: 6人
不明: 0人

【詳細情報】
人物1: エリアC (信頼度: 0.925, 位置: (266.2, 514.1))
人物2: エリアC (信頼度: 0.905, 位置: (68.3, 436.9))
...
```

---

## 🎨 可視化サンプル

* エリアはポリゴンで色分け表示
* 各人物の足元に識別番号と色付きの点を表示
* 出力番号、信頼度、座標など一覧化

```python
counter.visualize_areas_and_detections(sample_bboxes)
# または画像保存：
counter.visualize_areas_and_detections(sample_bboxes, save_path="result.png")
```

---

## ⚙️ カスタマイズ

### エリア定義の変更

```python
self.areas = {
    'Area A': {
        'polygon': [(400, 0), (1024, 0), (1024, 300), (600, 200), (400, 200)]
    },
    ...
}
```

### 画像サイズの設定

```python
counter = AreaPersonCounter(image_width=1024, image_height=576)
```

---

## 📁 サンプル入力フォーマット

```json
{
  "x1": 100,
  "y1": 200,
  "x2": 150,
  "y2": 350,
  "confidence": 0.85,
  "classId": 0
}
```

* `x1, y1`: 左上の座標
* `x2, y2`: 右下の座標
* `confidence`: 検出の信頼度 (0.0 − 1.0)

---

## ⚠️ 注意事項

* エリア判定は人物の「足元」に基づいています
* 境界付近にいる場合は誤分類されることがあります
* エリアの座標は画像ごとに調整してください

---

## 🧑‍💻 作成者

Keisuke Iwasaki (example)

ご意見やPRは歓迎です！

---
