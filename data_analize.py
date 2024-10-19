import sqlite3
import math
from datetime import datetime


# Функция для расчета Евклидова расстояния между двумя точками
def calculate_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


# Функция для расчета скорости (distance/time)
def calculate_speed(distance, time_diff_sec):
    if time_diff_sec == 0:
        return 0
    return distance / time_diff_sec


# Функция для расчета угла (поворота) между двумя точками
def calculate_rotation(x1, y1, x2, y2):
    return math.atan2(y2 - y1, x2 - x1)


# Функция для разбора временных меток
def parse_timestamp(timestamp_str):
    return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')


conn = sqlite3.connect('pose_data.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS analysis_data")

cursor.execute('''
CREATE TABLE IF NOT EXISTS analysis_data (
    frame_id INTEGER,
    keypoint_index INTEGER,
    speed REAL,
    rotation REAL,
    timestamp TEXT
)
''')
conn.commit()

cursor.execute('''
SELECT frame_id, keypoint_index, x_coord, y_coord, timestamp
FROM keypoint_data 
ORDER BY frame_id, keypoint_index
''')

data = cursor.fetchall()

keypoint_data = {}

for row in data:
    frame_id, keypoint_index, x, y, timestamp = row
    if keypoint_index not in keypoint_data:
        keypoint_data[keypoint_index] = []
    keypoint_data[keypoint_index].append({
        'frame_id': frame_id,
        'x': x,
        'y': y,
        'timestamp': timestamp
    })

# Анализ движения и угла поворота для ключевой точки 11 (например, левое бедро)
keypoint_id = 11
movement_data = keypoint_data[keypoint_id]

for i in range(1, len(movement_data)):
    current = movement_data[i]
    previous = movement_data[i - 1]

    x1, y1 = previous['x'], previous['y']
    x2, y2 = current['x'], current['y']

    time1 = parse_timestamp(previous['timestamp'])
    time2 = parse_timestamp(current['timestamp'])

    time_diff = (time2 - time1).total_seconds()

    if time_diff == 0:
        print(f"Пропуск кадра {current['frame_id']} из-за нулевой разницы во времени")
        continue

    distance = calculate_distance(x1, y1, x2, y2)
    speed = calculate_speed(distance, time_diff)

    cursor.execute('''
    INSERT INTO analysis_data (frame_id, keypoint_index, speed, rotation, timestamp)
    VALUES (?, ?, ?, ?, ?)
    ''', (current['frame_id'], keypoint_id, speed, None, current['timestamp']))

# Анализ углов поворота с использованием ключевых точек 11 (левое плечо) и 12 (правое плечо)
left_shoulder_data = keypoint_data[11]
right_shoulder_data = keypoint_data[12]

for i in range(1, len(left_shoulder_data)):
    ls_current = left_shoulder_data[i]
    rs_current = right_shoulder_data[i]

    x1, y1 = ls_current['x'], ls_current['y']
    x2, y2 = rs_current['x'], rs_current['y']

    rotation = calculate_rotation(x1, y1, x2, y2)
    rotation_degrees = math.degrees(rotation)

    cursor.execute('''
    INSERT INTO analysis_data (frame_id, keypoint_index, speed, rotation, timestamp)
    VALUES (?, ?, ?, ?, ?)
    ''', (ls_current['frame_id'], 11, None, rotation_degrees, ls_current['timestamp']))

conn.commit()
conn.close()

print("Анализ данных завершен и результаты записаны в базу данных.")
