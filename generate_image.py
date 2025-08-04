import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# CSVファイルの読み込み
csv_path = 'C:\\Users\\keisu\\Desktop\\function\\function\\output\\考察\\camera5.csv'
df = pd.read_csv(csv_path)

# CSVファイル名を取得（拡張子なし）
csv_filename = os.path.splitext(os.path.basename(csv_path))[0]

# 時間列をdatetime形式に変換（時分秒のみ）
df['time_parsed'] = pd.to_datetime(df['time'], format='%H:%M:%S')

# 誤差の絶対値を計算
df['abs_difference'] = abs(df['Difference'])

# 時間順にソート
df = df.sort_values('time_parsed')

# 時間順にソートしたユニークな時間リストを作成
unique_times = df.sort_values('time_parsed')['time'].unique()

# エリアごとにピボットテーブルを作成
pivot_df = df.pivot(index='time', columns='area', values='abs_difference')
pivot_df = pivot_df.fillna(0)  # NaNを0で埋める

# 時間順に並び替え
pivot_df = pivot_df.reindex(unique_times)

# 日本語フォントの設定（コメントアウト可能）
plt.rcParams['font.family'] = 'DejaVu Sans'

# グラフのサイズを設定
plt.figure(figsize=(14, 8))

# 積み上げ棒グラフの作成
areas = pivot_df.columns
colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
bottom = np.zeros(len(pivot_df))

bars = []
for i, area in enumerate(areas):
    bar = plt.bar(range(len(pivot_df)), pivot_df[area], 
                  bottom=bottom, label=f'Area {area}', 
                  color=colors[i % len(colors)], alpha=0.8)
    bars.append(bar)
    bottom += pivot_df[area]

# グラフの装飾
plt.title(f'{csv_filename}: YOLO vs Manual Count Error Analysis by Area and Time\n(Absolute Difference Stacked Bar Chart)', 
          fontsize=16, fontweight='bold', pad=20)
plt.xlabel('Time', fontsize=12, fontweight='bold')
plt.ylabel('Absolute Difference (People Count)', fontsize=12, fontweight='bold')

# X軸のラベルを時間に設定（時間順になっている）
sorted_time_objects = sorted(pd.to_datetime(pivot_df.index, format='%H:%M:%S'))
time_labels = [t.strftime('%H:%M') for t in sorted_time_objects]
plt.xticks(range(len(pivot_df)), time_labels, rotation=45, ha='right')

# 凡例の設定
plt.legend(title='Areas', bbox_to_anchor=(1.05, 1), loc='upper left')

# グリッドの追加
plt.grid(axis='y', alpha=0.3, linestyle='--')

# レイアウトの調整
plt.tight_layout()

# 統計情報をテキストとして追加
total_error = df['abs_difference'].sum()
avg_error = df['abs_difference'].mean()
plt.figtext(0.02, 0.02, f'Total Absolute Error: {total_error:.0f} | Average Error: {avg_error:.2f}', 
            fontsize=10, ha='left')

# 画像の保存
output_path = 'C:\\Users\\keisu\\Desktop\\function\\function\\output\\考察\\yolo_error_stacked_chart.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"グラフが保存されました: {output_path}")

# グラフを表示
plt.show()

# データの詳細分析も表示
print("\n=== エリア別誤差統計 ===")
area_stats = df.groupby('area').agg({
    'abs_difference': ['sum', 'mean', 'std', 'max'],
    'Difference': ['mean']
}).round(2)
print(area_stats)

print("\n=== 時間別合計誤差 ===")
time_stats = df.groupby('time')['abs_difference'].sum().sort_values(ascending=False)
print(time_stats)