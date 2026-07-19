import cv2
import mediapipe as mp
import numpy as np
import pygame
import os
from pydub import AudioSegment
import ffmpeg

# --- 音の初期化 ---
pygame.mixer.init()
sound_file = "ban.wav"
sound = pygame.mixer.Sound(sound_file)

# --- MediaPipe初期化 ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- 動画読み込み ---
input_video = "A_1.mp4"
cap = cv2.VideoCapture(input_video)

# --- 動画書き出し設定 ---
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
temp_video = "temp_video.mp4"
out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

# --- 動作検出用変数 ---
prev_dist = {"RIGHT": None, "LEFT": None}
prev_time = None
velocity_threshold = 1.087  # 音鳴らし判定の閾値
min_interval = 0            # 音を鳴らす最短間隔
last_sound_time = 0
ready_to_play = {"RIGHT": False, "LEFT": False}  # フラグ

# --- 音声イベント記録 ---
sound_events = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # --- 映像を上下反転 ---
    frame = cv2.flip(frame, 0)

    # --- MediaPipe処理 ---
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
    play_sound = False

    if results.pose_landmarks:
        for side in ["RIGHT", "LEFT"]:
            wrist_id = mp_pose.PoseLandmark.RIGHT_WRIST if side == "RIGHT" else mp_pose.PoseLandmark.LEFT_WRIST
            shoulder_id = mp_pose.PoseLandmark.RIGHT_SHOULDER if side == "RIGHT" else mp_pose.PoseLandmark.LEFT_SHOULDER

            wrist = results.pose_landmarks.landmark[wrist_id]
            shoulder = results.pose_landmarks.landmark[shoulder_id]

            # 手首と肩の距離
            dist = np.sqrt((wrist.x - shoulder.x)**2 + (wrist.y - shoulder.y)**2)

            # ベロシティ計算
            if prev_dist[side] is not None and prev_time is not None:
                dt = current_time - prev_time
                if dt > 0:
                    velocity = (dist - prev_dist[side]) / dt

                    # --- フラグ管理 ---
                    if velocity > velocity_threshold:
                        ready_to_play[side] = True

                    if ready_to_play[side] and velocity <= 0:
                        play_sound = True
                        ready_to_play[side] = False

            prev_dist[side] = dist

        prev_time = current_time

    # --- 音再生 ---
    if play_sound and (current_time - last_sound_time) > min_interval:
        print(f"🎵 音再生: {current_time:.2f}s")
        sound.play()
        last_sound_time = current_time
        sound_events.append((current_time, sound_file))

    # --- 動画出力 ---
    out.write(image)

    # --- プレビュー（任意） ---
    cv2.imshow("Velocity Trigger (Both Hands, Flipped)", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 後処理 ---
cap.release()
out.release()
cv2.destroyAllWindows()
pose.close()

print("✅ 一時動画出力完了:", temp_video)
print("🎵 音イベント数:", len(sound_events))

# --- 音声付き動画作成 ---
final_audio = AudioSegment.silent(duration=int(current_time * 1000))
sound_segment = AudioSegment.from_file(sound_file)

for t, _ in sound_events:
    start_ms = int(t * 1000)
    final_audio = final_audio.overlay(sound_segment, position=start_ms)

temp_audio = "temp_audio.wav"
final_audio.export(temp_audio, format="wav")

final_video = "output_with_sound_A_1_1.mp4"

# --- ffmpegで統合（上下反転済み映像＋音声） ---
video_input = ffmpeg.input(temp_video)
audio_input = ffmpeg.input(temp_audio)

ffmpeg.output(
    video_input,
    audio_input,
    final_video,
    vcodec='copy',
    acodec='aac',
    strict='experimental'
).run(overwrite_output=True)

print("✅ 出力完了:", final_video)

# --- 一時ファイル削除 ---
os.remove(temp_video)
os.remove(temp_audio)



# 音再生: 1.77s
# 音再生: 2.14s
# 音再生: 2.54s
# 音再生: 2.97s
# 音再生: 3.40s