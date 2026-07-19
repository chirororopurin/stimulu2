import cv2
import mediapipe as mp
import numpy as np
import pygame
import os
from pydub import AudioSegment
import ffmpeg
import random

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
temp_video = "temp_video_weak.mp4"
out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

# --- 動作検出用変数（今回は使わない） ---
prev_dist = {"RIGHT": None, "LEFT": None}
prev_time = None

# --- 音声イベント記録 ---
sound_events = []

# --- ランダム音再生タイミング生成 ---
# 動画の長さ（秒）に基づきランダムに5回音を鳴らす
video_length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps
num_sounds = 5
random_times = sorted([random.uniform(0, video_length) for _ in range(num_sounds)])
sound_index = 0

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

    # --- ランダムタイミングで音再生 ---
    play_sound = False
    if sound_index < num_sounds and current_time >= random_times[sound_index]:
        play_sound = True
        sound_index += 1

    if play_sound:
        print(f"🎵 音再生 (弱マッピング): {current_time:.2f}s")
        sound.play()
        sound_events.append((current_time, sound_file))

    # --- 動画出力 ---
    out.write(image)

    # --- プレビュー（任意） ---
    cv2.imshow("Weak Mapping Random Sound", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

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

temp_audio = "temp_audio_weak.wav"
final_audio.export(temp_audio, format="wav")

final_video = "output_with_sound_1_2.mp4"

# --- ffmpegで統合 ---
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


# 音再生 (弱マッピング): 0.07s
# 音再生 (弱マッピング): 1.20s
# 音再生 (弱マッピング): 2.30s
# 音再生 (弱マッピング): 3.20s
# 音再生 (弱マッピング): 4.30s