import pandas as pd
import cv2
import numpy as np
import json
import os
from datetime import datetime
from typing import Dict, List, Tuple
import glob

class DetectionAnalyzer:
    def __init__(self):
        # デバイスごとのエリア定義
        self.device_areas = {
            'b593f5cd66edab03': {
                'Area A': {
                    'polygon': [(2057, 2240), (3215, 2288), (3305, 1371), (2208, 1312)]
                },
                'Area B': {
                    'polygon': [(1390, 1370), (708, 1572), (0, 1264), (0, 1087), (607, 1090)]
                },
                'Area C': {
                    'polygon': [(2057, 2240), (2208, 1312), (1390, 1370), (708, 1572), (0, 1264), (0, 2240)]
                },
                'Area D': {
                    'polygon': [(1911, 3120), (2057, 2240), (0, 2240), (0, 3120)]
                }
            },
            '960afb85792f1633': {
                'Area A': {
                    'polygon': [(4160, 2386), (4160, 1387), (3812, 1387), (3582, 2254)]
                },
                'Area B': {
                    'polygon': [(3000, 1320), (2301, 1500), (1818, 1242), (1799, 1068), (2393, 1068)]
                },
                'Area C': {
                    'polygon': [(3582, 2254), (3812, 1387), (3000, 1320), (2301, 1500), (1818, 1242), (624, 1284), (921, 1609)]
                },
                'Area D': {
                    'polygon': [(3582, 2254), (921, 1609), (0, 1786), (0, 3120), (3268, 3120)]
                },
                'Area E': {
                    'polygon': [(921, 1609), (624, 1284), (455, 1000), (0, 998), (0, 1786)]
                }
            },
            'f2a02747dd65c8d1': {
                'Area A': {
                    'polygon': [(2281, 521), (2337, 235), (1314, 201)]
                },
                'Area C': {
                    'polygon': [(2281, 521), (1314, 201), (565, 190), (615, 456), (0, 378), (0, 824), (792, 790)]
                },
                'Area D': {
                    'polygon': [(2281, 521), (792, 790), (1577, 1718), (3313, 1070)]
                },
                'Area E': {
                    'polygon': [(0, 824), (792, 790), (1577, 1718), (792, 3120), (0, 3120)]
                },
                'Area F': {
                    'polygon': [(1577, 1718), (3313, 1070), (4160, 1399), (4160, 3120), (792, 3120)]
                }
            },
            'afcc7a113c41f44e': {
                'Area A': {
                    'polygon': [(523, 824), (419, 518), (0, 496), (0, 784)]
                },
                'Area D': {
                    'polygon': [(0, 784), (0, 3120), (1692, 874), (523, 824)]
                },
                'Area F': {
                    'polygon': [(0, 3120), (1692, 874), (4160, 804), (4160, 1892), (1771, 2953)]
                }
            }
        }
        
        # 画像とバウンディングボックスの縮尺設定
        self.image_size = (4160, 3120)
        self.bbox_size = (1024, 768)
        self.scale_x = self.image_size[0] / self.bbox_size[0]
        self.scale_y = self.image_size[1] / self.bbox_size[1]

    def parse_datetime_from_utc(self, utc_str: str) -> Tuple[str, str]:
        """UTC文字列から日付と時刻を抽出"""
        dt = datetime.fromisoformat(utc_str.replace(' UTC', '+00:00'))
        date_str = dt.strftime('%Y%m%d')
        time_str = dt.strftime('%H%M%S')
        return date_str, time_str

    def find_image_file(self, device_id: str, date_str: str, time_str: str, loop_count: int, image_dir: str) -> str:
        """画像ファイルを検索（時間のズレを考慮）"""
        loop_count_padded = f"{loop_count:010d}"
        
        # 基本的なファイル名パターン
        base_pattern = f"{device_id}_{device_id}_{date_str}_{time_str}_{loop_count_padded}.jpg"
        base_path = os.path.join(image_dir, base_pattern)
        
        if os.path.exists(base_path):
            return base_path
        
        # 時間のズレを考慮して検索（±10秒）
        base_time = datetime.strptime(f"{date_str}{time_str}", '%Y%m%d%H%M%S')
        
        for offset in range(-10, 11):
            adjusted_time = base_time + pd.Timedelta(seconds=offset)
            adjusted_time_str = adjusted_time.strftime('%H%M%S')
            adjusted_pattern = f"{device_id}_{device_id}_{date_str}_{adjusted_time_str}_{loop_count_padded}.jpg"
            adjusted_path = os.path.join(image_dir, adjusted_pattern)
            
            if os.path.exists(adjusted_path):
                return adjusted_path
        
        return None

    def scale_bbox_to_image(self, bbox: Dict) -> Dict:
        """バウンディングボックスを画像座標にスケール"""
        # NaNチェックを追加
        if (pd.isna(bbox['x1']) or pd.isna(bbox['y1']) or 
            pd.isna(bbox['x2']) or pd.isna(bbox['y2'])):
            return None
            
        return {
            'x1': int(bbox['x1'] * self.scale_x),
            'y1': int(bbox['y1'] * self.scale_y),
            'x2': int(bbox['x2'] * self.scale_x),
            'y2': int(bbox['y2'] * self.scale_y),
            'confidence': bbox['confidence'],
            'classId': bbox['classId']
        }

    def point_in_polygon(self, point: Tuple[float, float], polygon: List[Tuple[int, int]]) -> bool:
        """点がポリゴン内にあるかチェック（Ray casting algorithm）"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside

    def count_people_in_areas(self, bboxes: List[Dict], device_id: str) -> Dict[str, int]:
        """エリア別人数カウント"""
        if device_id not in self.device_areas:
            return {}
        
        areas = self.device_areas[device_id]
        area_counts = {area_name: 0 for area_name in areas.keys()}
        
        for bbox in bboxes:
            # バウンディングボックスの底辺中点を計算
            bottom_center_x = (bbox['x1'] + bbox['x2']) / 2
            bottom_center_y = bbox['y2']
            point = (bottom_center_x, bottom_center_y)
            
            # 各エリアをチェック
            for area_name, area_data in areas.items():
                if self.point_in_polygon(point, area_data['polygon']):
                    area_counts[area_name] += 1
                    break  # 最初に見つかったエリアのみカウント
        
        return area_counts

    def draw_visualization(self, image_path: str, bboxes: List[Dict], device_id: str, output_path: str):
        """バウンディングボックスとエリアを描画"""
        if not os.path.exists(image_path):
            print(f"画像ファイルが見つかりません: {image_path}")
            return
        
        # 画像読み込み
        img = cv2.imread(image_path)
        if img is None:
            print(f"画像の読み込みに失敗しました: {image_path}")
            return
        
        # エリアを描画
        # エリア名に応じた固定色を定義（ここで統一）
        area_colors = {
            'Area A': (255, 102, 102),   # 赤
            'Area B': (102, 255, 102),   # 緑
            'Area C': (102, 178, 255),   # 青
            'Area D': (255, 255, 102),   # 黄
            'Area E': (255, 153, 255),   # ピンク
            'Area F': (153, 255, 255)    # 水色
        }

        # ↓ この部分を以下のように変更
        for area_name, area_data in self.device_areas[device_id].items():
            color = area_colors.get(area_name, (200, 200, 200))  # 未定義のエリア名はグレー
            
            pts = np.array(area_data['polygon'], np.int32).reshape((-1, 1, 2))
            cv2.polylines(img, [pts], True, color, thickness=8)

            centroid = np.mean(area_data['polygon'], axis=0).astype(int)
            cv2.putText(img, area_name, tuple(centroid),
                        cv2.FONT_HERSHEY_SIMPLEX, fontScale=3, color=color, thickness=5)


        
        # バウンディングボックスを描画
        for bbox in bboxes:
            # バウンディングボックス
            cv2.rectangle(img, (bbox['x1'], bbox['y1']), (bbox['x2'], bbox['y2']), (0, 255, 255), 3)  # 黄色
            
            # 信頼度を表示
            #cv2.putText(img, f"{bbox['confidence']:.2f}", 
            #           (bbox['x1'], bbox['y1'] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # 底辺中点を描画
            bottom_center_x = int((bbox['x1'] + bbox['x2']) / 2)
            bottom_center_y = bbox['y2']
            cv2.circle(img, (bottom_center_x, bottom_center_y), 10, (0, 0, 255), -1)
        
        # 結果を保存
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)

    def process_csv(self, csv_file_path: str, image_dir: str, output_dir: str, area_count_output: str):
        """CSVファイルを処理してエリア別人数カウントと可視化を実行"""
        # CSVファイル読み込み
        df = pd.read_csv(csv_file_path)
        
        # 画像ごとにデータをグループ化
        image_groups = df.groupby(['document_id', 'deviceId', 'jst_createdAt', 'loopCount'])
        
        results = []
        
        for (doc_id, device_id, created_at, loop_count), group in image_groups:
            print(f"処理中: {device_id}, {created_at}, {loop_count}")
            
            # 日付と時刻を抽出
            date_str, time_str = self.parse_datetime_from_utc(created_at)
            
            # 画像ファイルを検索
            image_path = self.find_image_file(device_id, date_str, time_str, loop_count, image_dir)
            
            if image_path is None:
                print(f"画像ファイルが見つかりません: {device_id}_{date_str}_{time_str}_{loop_count}")
                continue
            
            # バウンディングボックスデータを処理
            bboxes = []
            for _, row in group.iterrows():
                # NaNをチェックしてスキップ
                if (pd.isna(row['x1']) or pd.isna(row['y1']) or 
                    pd.isna(row['x2']) or pd.isna(row['y2'])):
                    print(f"NaN値を検出、スキップ: {row.name}")
                    continue
                    
                bbox = {
                    'x1': row['x1'],
                    'y1': row['y1'],
                    'x2': row['x2'],
                    'y2': row['y2'],
                    'confidence': row['confidence'],
                    'classId': row['classId']
                }
                # 画像座標にスケール
                scaled_bbox = self.scale_bbox_to_image(bbox)
                if scaled_bbox is not None:  # NaNチェック後の結果を確認
                    bboxes.append(scaled_bbox)
            
            # エリア別人数カウント
            area_counts = self.count_people_in_areas(bboxes, device_id)
            
            # 結果を記録
            result = {
                'document_id': doc_id,
                'deviceId': device_id,
                'jst_createdAt': created_at,
                'loopCount': loop_count,
                'total_detections': len(bboxes),
                'image_path': image_path
            }
            result.update(area_counts)
            results.append(result)
            
            # 可視化画像を生成
            output_filename = f"{device_id}_{date_str}_{time_str}_{loop_count:010d}_annotated.jpg"
            output_path = os.path.join(output_dir, output_filename)
            self.draw_visualization(image_path, bboxes, device_id, output_path)
            
            print(f"完了: {output_filename}, エリア別人数: {area_counts}")
        
        # 結果をCSVに保存
        results_df = pd.DataFrame(results)
        os.makedirs(os.path.dirname(area_count_output), exist_ok=True)
        results_df.to_csv(area_count_output, index=False, encoding='utf-8-sig')
        
        print(f"エリア別人数カウント結果を保存: {area_count_output}")
        print(f"可視化画像を保存: {output_dir}")
        
        return results_df

def main():
    # パス設定
    csv_file_path = "C:\\Users\\keisu\\Desktop\\function\\function\\data\\20250725_目視確認画像に対応した検知結果.csv"
    image_dir = "./data/picture"
    output_dir = "C:\\Users\\keisu\\Desktop\\function\\function\\output\\BB"
    area_count_output = "C:\\Users\\keisu\\Desktop\\function\\function\\output\\area_count_results.csv"
    
    # アナライザー初期化
    analyzer = DetectionAnalyzer()
    
    # 処理実行
    results = analyzer.process_csv(
        csv_file_path=csv_file_path,
        image_dir=image_dir,
        output_dir=output_dir,
        area_count_output=area_count_output
    )
    
    print("処理完了!")
    print(f"総画像数: {len(results)}")
    if len(results) > 0:
        print(f"結果の例:")
        print(results.head())

if __name__ == "__main__":
    main()

