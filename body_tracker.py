import cv2
import mediapipe as mp
import sqlite3
import time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

read_frequency_ms = 500

conn = sqlite3.connect('pose_data.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS keypoint_data (
    frame_id INTEGER,
    keypoint_index INTEGER,
    x_coord REAL,
    y_coord REAL,
    timestamp TEXT
)
''')
conn.commit()

frame_id = 0

while cap.isOpened():
    start_time = time.time()

    ret, frame = cap.read()
    if not ret:
        print("Не удалось получить кадр")
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(rgb_frame)

    if results.pose_landmarks:
        mp_drawing.draw_landmarks(
            frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        for idx, landmark in enumerate(results.pose_landmarks.landmark):
            h, w, _ = frame.shape  # Размеры кадра
            cx, cy = int(landmark.x * w), int(landmark.y * h)

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

            print(f'Кадр {frame_id}, Ключевой пункт {idx}: (x: {cx}, y: {cy})')

            cursor.execute('''
            INSERT INTO keypoint_data (frame_id, keypoint_index, x_coord, y_coord, timestamp)
            VALUES (?, ?, ?, ?, ?)
            ''', (frame_id, idx, cx, cy, timestamp))

            cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

        conn.commit()

    cv2.imshow('Обнаружение позы', frame)

    frame_id += 1

    elapsed_time = (time.time() - start_time) * 1000  # Перевод в миллисекунды

    wait_time = int(max(1, read_frequency_ms - elapsed_time))  # Обеспечение положительного времени ожидания
    if cv2.waitKey(wait_time) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

conn.close()
