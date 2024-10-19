import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime


def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')


conn = sqlite3.connect('pose_data.db')
cursor = conn.cursor()

cursor.execute('''
SELECT frame_id, speed, timestamp 
FROM analysis_data
WHERE keypoint_index = 11 AND speed IS NOT NULL
ORDER BY frame_id
''')
speed_data = cursor.fetchall()

cursor.execute('''
SELECT frame_id, rotation, timestamp 
FROM analysis_data
WHERE keypoint_index = 11 AND rotation IS NOT NULL
ORDER BY frame_id
''')
rotation_data = cursor.fetchall()

conn.close()

# График скорости движения ключевой точки 11 (например, левое бедро)
frame_ids_speed = [row[0] for row in speed_data]  # frame_id для скорости
speeds = [row[1] for row in speed_data]  # Скорость
timestamps_speed = [parse_timestamp(row[2]) for row in speed_data]  # Временные метки

plt.figure(figsize=(10, 5))
plt.plot(timestamps_speed, speeds, label='Speed of left hip (keypoint 11)', color='blue', marker='o')
plt.title('Speed of Movement over Time')
plt.xlabel('Time')
plt.ylabel('Speed (pixels/sec)')
plt.xticks(rotation=45)  # Поворот меток оси X для удобства чтения времени
plt.tight_layout()
plt.legend()
plt.grid(True)
plt.show()

# График углов поворота ключевой точки 11 (например, угол между плечами)
frame_ids_rotation = [row[0] for row in rotation_data]  # frame_id для углов
rotations = [row[1] for row in rotation_data]  # Углы поворота
timestamps_rotation = [parse_timestamp(row[2]) for row in rotation_data]  # Временные метки

plt.figure(figsize=(10, 5))
plt.plot(timestamps_rotation, rotations, label='Rotation between shoulders', color='green', marker='o')
plt.title('Rotation between Shoulders over Time')
plt.xlabel('Time')
plt.ylabel('Rotation (degrees)')
plt.xticks(rotation=45)  # Поворот меток оси X для удобства чтения времени
plt.tight_layout()
plt.legend()
plt.grid(True)
plt.show()
