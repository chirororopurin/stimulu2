import cv2
import mediapipe as mp
import numpy as np
import pygame
import os
from pydub import AudioSegment
import ffmpeg

# --- 音の初期化 ---
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# --- MediaPipe初期化 ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- 動画設定 ---
input_video = "B_1.mp4"
cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
temp_video = "temp_video.mp4"
out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

# --- 音イベント記録 ---
sound_events = []

# --- パラメータ ---
prev_wrist = {"RIGHT": None, "LEFT": None}
prev_time = None
frame_count = {"RIGHT": 0, "LEFT": 0}
frame_interval = 3         # 3フレームごとに音を鳴らす
vel_threshold = 0.1      # vx の閾値
sample_rate = 44100
duration = 0.25            # 音の長さ（秒）
freq_step = 20.0           # vxの符号で増減するHz
freq_current = {"RIGHT": 440.0, "LEFT": 440.0}
min_freq = 220.0
max_freq = 1320.0

# --- 柔らかいハープ音生成関数 ---
def generate_harp_tone(frequency=440.0, duration=0.25, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-4 * t)
    wave = (np.sin(2 * np.pi * frequency * t) * 0.7 +
            np.sin(2 * np.pi * frequency * 2 * t) * 0.3) * envelope
    wave = (wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(wave)

# --- メインループ ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 0)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

    if results.pose_landmarks:
        for side in ["RIGHT", "LEFT"]:
            wrist_id = mp_pose.PoseLandmark.RIGHT_WRIST if side == "RIGHT" else mp_pose.PoseLandmark.LEFT_WRIST
            wrist = results.pose_landmarks.landmark[wrist_id]

            x = wrist.x

            if prev_wrist[side] is not None and prev_time is not None:
                dt = current_time - prev_time
                if dt > 0:
                    vx = (x - prev_wrist[side])/ dt

                    # vxが閾値以上かつ3フレームごと
                    if abs(vx) > vel_threshold and frame_count[side] % frame_interval == 0:
                        if vx > 0:
                            freq_current[side] += freq_step
                        else:
                            freq_current[side] -= freq_step

                        # 音高範囲制限
                        freq_current[side] = np.clip(freq_current[side], min_freq, max_freq)

                        # 音を鳴らす
                        sound = generate_harp_tone(freq_current[side], duration, sample_rate)
                        sound.play()
                        sound_events.append((current_time, freq_current[side]))
                        print(f"🎵 {side}: freq={freq_current[side]:.1f}Hz, vx={vx:.4f}")

            prev_wrist[side] = x
            frame_count[side] += 1

    prev_time = current_time

    out.write(image)
    cv2.imshow("Harp Motion (Velocity-based Pitch, Independent)", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
pose.close()

print("✅ 一時動画出力完了:", temp_video)
print("🎵 音イベント数:", len(sound_events))

# --- 音声を合成 ---
final_audio = AudioSegment.silent(duration=int(current_time * 1000))
for t, freq in sound_events:
    t_arr = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-4 * t_arr)
    wave = (np.sin(2 * np.pi * freq * t_arr) * 0.7 +
            np.sin(2 * np.pi * freq * 2 * t_arr) * 0.3) * envelope
    wave = (wave * 32767).astype(np.int16)
    temp_sound = AudioSegment(
        wave.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1
    )
    final_audio = final_audio.overlay(temp_sound, position=int(t * 1000))

temp_audio = "temp_audio.wav"
final_audio.export(temp_audio, format="wav")

# --- ffmpegで統合 ---
final_video = "output_with_sound_B_1_1.mp4"
video_input = ffmpeg.input(temp_video)
audio_input = ffmpeg.input(temp_audio)
ffmpeg.output(video_input, audio_input, final_video, vcodec='copy', acodec='aac').run(overwrite_output=True)

print("✅ 出力完了:", final_video)

# --- 一時ファイル削除 ---
os.remove(temp_video)
os.remove(temp_audio)



# LEFT: freq=420.0Hz, vx=-0.4895
# LEFT: freq=400.0Hz, vx=-0.1483
# LEFT: freq=380.0Hz, vx=-0.1019
# LEFT: freq=400.0Hz, vx=0.1879
# LEFT: freq=420.0Hz, vx=0.1969
# LEFT: freq=440.0Hz, vx=0.4370
#  LEFT: freq=460.0Hz, vx=0.3239
#  LEFT: freq=480.0Hz, vx=0.2661
#  LEFT: freq=500.0Hz, vx=0.1281
#  LEFT: freq=480.0Hz, vx=-0.2871
#  LEFT: freq=460.0Hz, vx=-0.4223
#  LEFT: freq=440.0Hz, vx=-0.1468
#  LEFT: freq=420.0Hz, vx=-0.3524
#  LEFT: freq=400.0Hz, vx=-0.1236
#  LEFT: freq=380.0Hz, vx=-0.1160
#  LEFT: freq=400.0Hz, vx=0.1487
#  LEFT: freq=420.0Hz, vx=0.3480
#  LEFT: freq=440.0Hz, vx=0.2588
#  LEFT: freq=460.0Hz, vx=0.3799
#  LEFT: freq=480.0Hz, vx=0.1939
#  LEFT: freq=500.0Hz, vx=0.2314
#  LEFT: freq=520.0Hz, vx=0.1137
#  LEFT: freq=500.0Hz, vx=-0.2169
#  LEFT: freq=480.0Hz, vx=-0.2385
#  LEFT: freq=460.0Hz, vx=-0.3090
#  LEFT: freq=440.0Hz, vx=-0.3157
#  LEFT: freq=420.0Hz, vx=-0.2229
#  LEFT: freq=440.0Hz, vx=0.1261
#  RIGHT: freq=460.0Hz, vx=0.1493
#  RIGHT: freq=440.0Hz, vx=-0.2660
#  RIGHT: freq=420.0Hz, vx=-0.1213
#  RIGHT: freq=400.0Hz, vx=-0.2305
#  RIGHT: freq=380.0Hz, vx=-0.1679
#  RIGHT: freq=360.0Hz, vx=-0.1445
#  RIGHT: freq=340.0Hz, vx=-0.1742
#  RIGHT: freq=360.0Hz, vx=0.1770
#  RIGHT: freq=380.0Hz, vx=0.3112
#  RIGHT: freq=400.0Hz, vx=0.1075
#  RIGHT: freq=420.0Hz, vx=0.2033