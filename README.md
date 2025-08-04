# README

## 📁 概要

このプロジェクトは、YOLO物体検出で得られた人物検出結果を分析するための2つのPythonスクリプトで構成されています。
以下のタスクを実行します：

1. `count_pic_fiexed.py`：画像上の定義済みポリゴン領域ごとの検出人数をカウントし、結果を可視化します。
2. `generate_image.py`：YOLO検出と目視カウントの誤差（差分）を分析し、積み上げ棒グラフとして可視化します。

---

## 1. `count_pic_fiexed.py`

### 🔧 機能

* YOLO検出結果のCSVファイルを読み込み
* バウンディングボックスを画像座標にスケーリング
* 各検出がどのポリゴン領域に属するかを判定
* 画像ごとに領域別の人数をカウント
* バウンディングボックスとエリアを画像上に描画
* アノテーション済み画像と要約CSVを保存

### ✍️ 使い方

```bash
python count_pic_fiexed.py
```

### 📂 入力

* CSVファイル：`csv_file_path` に設定されたパス
* 画像ディレクトリ：`image_dir` に設定されたパス

### 📤 出力

* バウンディングボックスとエリア描画済み画像：`output_dir` に保存
* エリア別カウント結果CSV：`area_count_output` に保存

### ⚙️ 設定

`main()` 関数内の以下の変数を適宜変更してください：

```python
csv_file_path = "path/to/detection_results.csv"
image_dir = "path/to/image_directory"
output_dir = "path/to/output_directory"
area_count_output = "path/to/area_count_results.csv"
```

### ✅ 特徴

* 複数のデバイスIDに対応したポリゴンエリア定義
* Ray-casting アルゴリズムによる領域判定
* ±10秒の時刻誤差を考慮したファイル検索
* スケーリングされたバウンディングボックス描画
* OpenCVによる可視化処理

### 🔍 出力例

* アノテーション画像名：`deviceID_date_time_loopCount_annotated.jpg`
* 結果CSV名：`area_count_results.csv`

---

## 2. `generate_image.py`

### 🔧 機能

* 人数比較CSVを読み込み
* YOLO検出と目視カウントの誤差（絶対値）を算出
* 時間×エリアごとの誤差を積み上げ棒グラフとして表示
* 統計情報をPNGとして保存＋ターミナルに出力

### ✍️ 使い方

```bash
python generate_image.py
```

### 📂 入力

* 以下のカラムを含むCSVファイル：

  * `time`, `area`, `Difference`

CSVの例：

```
time, area, 目視人数, YOLO検出人数, Difference
12:00:00, A, 10, 8, -2
...
```

### 📤 出力

* 積み上げ棒グラフPNG：`output_path` に保存
* ターミナル：領域別および時間別の統計情報を表示

### ⚙️ 設定

以下の変数を変更してください：

```python
csv_path = "path/to/your_input.csv"
output_path = "path/to/save/stacked_chart.png"
```

### ✅ 特徴

* `Difference` の絶対値を誤差として計算
* 領域別に色分けされた積み上げ棒グラフ
* 時刻順にX軸ラベルを整形
* 領域別・時刻別の統計情報を表示

### 📊 出力例

![Stacked Error Chart](./output/stacked_chart.png) *(画像が存在する場合)*

---

## 📚 必要なライブラリ

```bash
pip install pandas numpy opencv-python matplotlib
```

---

## 📅 作者

岩崎 圭佑

---

