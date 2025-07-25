import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon
import numpy as np

class AreaPersonCounter:
    def __init__(self, image_width=1024, image_height=576):
        """
        エリア別人数カウンター
        
        Args:
            image_width: 画像の幅
            image_height: 画像の高さ
        """
        self.image_width = image_width
        self.image_height = image_height
        
        # エリア定義（画像から読み取った大まかな境界）
        # 実際の画像に合わせて調整が必要
        self.areas = {
            'エリアB': {  # 左上の階段エリア
                'polygon': [(0, 0), (400, 0), (400, 200), (0, 280)]
            },
            'エリアC': {  # 左下の広場エリア
                'polygon': [(0, 280), (400, 200), (400, 576), (0, 576)]
            },
            'エリアA': {  # 右上の境内エリア
                'polygon': [(400, 0), (1024, 0), (1024, 300), (600, 200), (400, 200)]
            },
            'エリアD': {  # 右下の人物エリア
                'polygon': [(400, 576), (400, 200), (600, 200), (1024, 300), (1024, 576)]
            }
        }
    
    def point_in_polygon(self, point, polygon):
        """
        点がポリゴン内にあるかを判定（レイキャスティング法）
        
        Args:
            point: (x, y) 座標
            polygon: ポリゴンの頂点リスト
            
        Returns:
            bool: ポリゴン内にある場合True
        """
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
    
    def get_bbox_bottom_center(self, bbox):
        """
        バウンディングボックスの底辺中点を計算
        
        Args:
            bbox: {"x1": float, "y1": float, "x2": float, "y2": float, ...}
            
        Returns:
            tuple: (x, y) 底辺中点の座標
        """
        x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
        center_x = (x1 + x2) / 2
        bottom_y = max(y1, y2)  # y座標の大きい方が下
        return (center_x, bottom_y)
    
    def classify_person_to_area(self, bbox):
        """
        バウンディングボックスをエリアに分類
        
        Args:
            bbox: バウンディングボックス辞書
            
        Returns:
            str: エリア名（該当なしの場合は"不明"）
        """
        bottom_center = self.get_bbox_bottom_center(bbox)
        
        for area_name, area_info in self.areas.items():
            if self.point_in_polygon(bottom_center, area_info['polygon']):
                return area_name
        
        return "不明"
    
    def count_people_by_area(self, bboxes):
        """
        バウンディングボックスリストからエリア別人数をカウント
        
        Args:
            bboxes: バウンディングボックスのリスト
            
        Returns:
            dict: エリア別の人数とdetails
        """
        area_counts = {area: 0 for area in self.areas.keys()}
        area_counts["不明"] = 0
        
        details = []
        
        for i, bbox in enumerate(bboxes):
            area = self.classify_person_to_area(bbox)
            area_counts[area] += 1
            
            bottom_center = self.get_bbox_bottom_center(bbox)
            details.append({
                'person_id': i + 1,
                'area': area,
                'bottom_center': bottom_center,
                'confidence': bbox.get('confidence', 0),
                'bbox': bbox
            })
        
        return {
            'area_counts': area_counts,
            'total_count': len(bboxes),
            'details': details
        }
    
    def visualize_areas_and_detections(self, bboxes, save_path=None):
        """
        エリア分割と検出結果を可視化
        
        Args:
            bboxes: バウンディングボックスのリスト
            save_path: 保存パス（Noneの場合は表示のみ）
        """
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        # エリアを色分けして表示
        colors = ['red', 'green', 'blue', 'orange', 'purple', 'brown']
        area_colors = {}
        
        for i, (area_name, area_info) in enumerate(self.areas.items()):
            color = colors[i % len(colors)]
            area_colors[area_name] = color
            
            polygon = Polygon(area_info['polygon'], alpha=0.3, 
                            facecolor=color, edgecolor=color, linewidth=2)
            ax.add_patch(polygon)
            
            # エリア名を表示
            centroid_x = sum(p[0] for p in area_info['polygon']) / len(area_info['polygon'])
            centroid_y = sum(p[1] for p in area_info['polygon']) / len(area_info['polygon'])
            ax.text(centroid_x, centroid_y, area_name, fontsize=12, 
                   ha='center', va='center', weight='bold')
        
        # バウンディングボックスと底辺中点を表示
        for i, bbox in enumerate(bboxes):
            x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
            
            # バウンディングボックス
            rect = patches.Rectangle((x1, y1), x2-x1, y2-y1, 
                                   linewidth=2, edgecolor='black', facecolor='none')
            ax.add_patch(rect)
            
            # 底辺中点
            bottom_center = self.get_bbox_bottom_center(bbox)
            area = self.classify_person_to_area(bbox)
            
            point_color = area_colors.get(area, 'gray')
            ax.plot(bottom_center[0], bottom_center[1], 'o', 
                   color=point_color, markersize=8, markeredgecolor='black')
            
            # 人物番号を表示
            ax.text(bottom_center[0], bottom_center[1] - 15, str(i+1), 
                   fontsize=10, ha='center', va='center', weight='bold', color='white',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor='black', alpha=0.7))
        
        ax.set_xlim(0, self.image_width)
        ax.set_ylim(self.image_height, 0)  # Y軸を反転
        ax.set_aspect('equal')
        ax.set_title('エリア分割と人物検出結果', fontsize=14, weight='bold')
        ax.grid(True, alpha=0.3)
        
        # 凡例
        legend_elements = [patches.Patch(facecolor=area_colors[area], 
                                       edgecolor=area_colors[area], 
                                       label=area) 
                         for area in self.areas.keys()]
        ax.legend(handles=legend_elements, loc='upper right')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.show()
    
    def generate_report(self, bboxes):
        """
        カウント結果のレポートを生成
        
        Args:
            bboxes: バウンディングボックスのリスト
            
        Returns:
            str: レポート文字列
        """
        result = self.count_people_by_area(bboxes)
        
        report = "=" * 50 + "\n"
        report += "エリア別人数カウント結果\n"
        report += "=" * 50 + "\n"
        report += f"総検出数: {result['total_count']}人\n\n"
        
        report += "【エリア別集計】\n"
        for area, count in result['area_counts'].items():
            report += f"{area}: {count}人\n"
        
        report += "\n【詳細情報】\n"
        for detail in result['details']:
            report += f"人物{detail['person_id']}: {detail['area']} "
            report += f"(信頼度: {detail['confidence']:.3f}, "
            report += f"位置: ({detail['bottom_center'][0]:.1f}, {detail['bottom_center'][1]:.1f}))\n"
        
        return report


# 使用例
if __name__ == "__main__":
    # サンプルデータ（提供されたバウンディングボックス）
    sample_bboxes = [
        {"x1":235.3131,"y1":375.89587,"x2":297.17224,"y2":514.0849,"confidence":0.9251581,"classId":0},
        {"x1":43.8387,"y1":337.0354,"x2":92.66295,"y2":436.88782,"confidence":0.90455294,"classId":0},
        {"x1":167.64896,"y1":341.54218,"x2":217.96207,"y2":439.49805,"confidence":0.88416696,"classId":0},
        {"x1":71.783104,"y1":298.5669,"x2":108.7875,"y2":379.95062,"confidence":0.87898666,"classId":0},
        {"x1":255.86105,"y1":346.19507,"x2":314.85825,"y2":436.51904,"confidence":0.8310888,"classId":0},
        {"x1":795.9126,"y1":366.331,"x2":844.7954,"y2":492.2691,"confidence":0.8190807,"classId":0},
        {"x1":963.44666,"y1":344.5509,"x2":986.43787,"y2":403.00714,"confidence":0.8038769,"classId":0},
        {"x1":527.7085,"y1":360.2514,"x2":560.94434,"y2":440.1726,"confidence":0.78461766,"classId":0},
        {"x1":133.94012,"y1":327.38797,"x2":186.94055,"y2":428.6061,"confidence":0.77629226,"classId":0},
        {"x1":686.8681,"y1":362.48224,"x2":724.368,"y2":438.33148,"confidence":0.7715475,"classId":0},
        {"x1":108.95944,"y1":309.08594,"x2":141.01889,"y2":382.27277,"confidence":0.73760056,"classId":0},
        {"x1":220.96533,"y1":321.98578,"x2":257.99817,"y2":402.72577,"confidence":0.7181517,"classId":0},
        {"x1":255.99098,"y1":323.48965,"x2":280.03674,"y2":397.86136,"confidence":0.67367595,"classId":0},
        {"x1":815.0513,"y1":349.37988,"x2":874.6344,"y2":467.61133,"confidence":0.61168045,"classId":0},
        {"x1":156.66153,"y1":331.26733,"x2":190.98486,"y2":417.85046,"confidence":0.5253996,"classId":0}
    ]
    
    # カウンターを初期化
    counter = AreaPersonCounter(image_width=1024, image_height=576)
    
    # エリア別人数をカウント
    result = counter.count_people_by_area(sample_bboxes)
    
    # レポート生成・表示
    report = counter.generate_report(sample_bboxes)
    print(report)
    
    # 可視化（実際の画像座標に合わせて調整が必要）
    counter.visualize_areas_and_detections(sample_bboxes)

