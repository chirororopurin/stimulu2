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
input_video = "B_1.mp4"     # 元動画 (Sliding × Correct × Narrow)
cap = cv2.VideoCapture(input_video)
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
temp_video = "temp_video.mp4"
out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

# --- 音イベント記録 ---
sound_events = []   # (time_sec, frequency)

# --- パラメータ ---
frame_interval = 3          # 3フレームごとに発音
vel_threshold = 0.1         # vx がこの値を超えたら発音
sample_rate = 44100
duration = 0.25             # 発音の長さ（秒）
freq_step = 20.0
min_freq = 220.0
max_freq = 1320.0

prev_wrist = {"RIGHT": None, "LEFT": None}
prev_time = None
frame_count = {"RIGHT": 0, "LEFT": 0}
freq_current = {"RIGHT": 440.0, "LEFT": 440.0}

# --- Timing offset 用ジッター ---
JITTER_MIN = -0.30  # ±150ms
JITTER_MAX = 0.30

# --- 柔らかいハープ音生成関数 ---
def generate_harp_tone(frequency=440.0, duration=0.25, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-4 * t)
    wave = (np.sin(2 * np.pi * frequency * t) * 0.7 +
            np.sin(2 * np.pi * frequency * 2 * t) * 0.3) * envelope
    wave = (wave * 32767).astype(np.int16)
    return pygame.sndarray.make_sound(wave)

# --- メインループ（動画処理） ---
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 0)
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0

    if results.pose_landmarks:
        for side in ["RIGHT", "LEFT"]:
            wrist_id = (mp_pose.PoseLandmark.RIGHT_WRIST if side == "RIGHT"
                        else mp_pose.PoseLandmark.LEFT_WRIST)
            wrist = results.pose_landmarks.landmark[wrist_id]

            x = wrist.x

            if prev_wrist[side] is not None and prev_time is not None:
                dt = current_time - prev_time
                if dt > 0:
                    vx = (x - prev_wrist[side]) / dt

                    # --- 発音条件 ---
                    if abs(vx) > vel_threshold and frame_count[side] % frame_interval == 0:
                        # pitch 変化
                        freq_current[side] += freq_step if vx > 0 else -freq_step
                        freq_current[side] = np.clip(freq_current[side], min_freq, max_freq)

                        # pygame 再生（プレビュー用）
                        tone = generate_harp_tone(freq_current[side], duration, sample_rate)
                        tone.play()

                        # 音イベント記録
                        sound_events.append((current_time, freq_current[side]))

                        print(f"🎵 {side} freq={freq_current[side]:.1f}Hz   vx={vx:.4f}")

            prev_wrist[side] = x
            frame_count[side] += 1

    prev_time = current_time

    out.write(image)
    cv2.imshow("Sliding Timing Offset Preview", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
pose.close()

print("🎥 一時動画出力:", temp_video)
print("🔊 発音イベント数:", len(sound_events))

# --- 音声合成（B方式: イベント間オフセットジッター） ---
final_audio = AudioSegment.silent(duration=int((current_time + 1) * 1000))

cumulative_offset = 0.0
jittered_events = []  # ジッター後の発生時刻を記録

for t, freq in sound_events:
    jitter = np.random.uniform(JITTER_MIN, JITTER_MAX)
    cumulative_offset += jitter
    jittered_time = max(t + cumulative_offset, 0.0)  # 負の時間にならないように

    # 波形生成
    t_arr = np.linspace(0, duration, int(sample_rate * duration), False)
    envelope = np.exp(-4 * t_arr)
    wave = (np.sin(2 * np.pi * freq * t_arr) * 0.7 +
            np.sin(2 * np.pi * freq * 2 * t_arr) * 0.3) * envelope
    wave = (wave * 32767).astype(np.int16)

    sound_seg = AudioSegment(
        wave.tobytes(), frame_rate=sample_rate, sample_width=2, channels=1
    )

    # ジッターを加えた時刻で重ね合わせ
    final_audio = final_audio.overlay(sound_seg, position=int(jittered_time * 1000))

    # ジッター後の実際の発生時刻を記録
    jittered_events.append((jittered_time, freq))

# --- 発生時刻を標準出力 ---
print("\n⚡ ジッター後の実際の発生時刻一覧:")
for jt, f in jittered_events:
    print(f"発生時刻={jt:.3f}s, freq={f:.1f}Hz")

# --- 音声の一時保存 ---
temp_audio = "temp_audio.wav"
final_audio.export(temp_audio, format="wav")

# --- 映像と合成 ---
final_video = "output_with_sound_B_1_3.mp4"
video_input = ffmpeg.input(temp_video)
audio_input = ffmpeg.input(temp_audio)
ffmpeg.output(video_input, audio_input, final_video, vcodec='copy', acodec='aac').run(overwrite_output=True)

print("🎬 完成動画:", final_video)

# --- 後片付け ---
os.remove(temp_video)
os.remove(temp_audio)




#⚡ ジッター後の実際の発生時刻一覧:
#発生時刻=0.354s, freq=420.0Hz
#発生時刻=0.652s, freq=400.0Hz
#発生時刻=0.664s, freq=380.0Hz
#発生時刻=0.931s, freq=400.0Hz
#発生時刻=1.067s, freq=420.0Hz
#発生時刻=1.263s, freq=440.0Hz
#発生時刻=1.482s, freq=460.0Hz
#発生時刻=1.515s, freq=480.0Hz
#発生時刻=1.448s, freq=500.0Hz
#発生時刻=2.432s, freq=480.0Hz
#発生時刻=2.662s, freq=460.0Hz
#発生時刻=2.825s, freq=440.0Hz
#発生時刻=3.009s, freq=420.0Hz
#発生時刻=3.181s, freq=400.0Hz
#発生時刻=3.104s, freq=380.0Hz
#発生時刻=3.553s, freq=400.0Hz
#発生時刻=3.679s, freq=420.0Hz
#発生時刻=3.719s, freq=440.0Hz
#発生時刻=4.017s, freq=460.0Hz
#発生時刻=4.369s, freq=480.0Hz
#発生時刻=4.635s, freq=500.0Hz
#発生時刻=4.749s, freq=520.0Hz
#発生時刻=5.231s, freq=500.0Hz
#発生時刻=5.134s, freq=480.0Hz
#発生時刻=5.406s, freq=460.0Hz
#発生時刻=5.383s, freq=440.0Hz
#発生時刻=5.846s, freq=420.0Hz
#発生時刻=6.596s, freq=440.0Hz
#発生時刻=6.923s, freq=460.0Hz
#発生時刻=7.451s, freq=440.0Hz
#発生時刻=7.333s, freq=420.0Hz
#発生時刻=7.164s, freq=400.0Hz
#発生時刻=7.251s, freq=380.0Hz
#発生時刻=7.291s, freq=360.0Hz
#発生時刻=7.242s, freq=340.0Hz
#発生時刻=7.964s, freq=360.0Hz
#発生時刻=7.882s, freq=380.0Hz
#発生時刻=8.065s, freq=400.0Hz
#発生時刻=8.395s, freq=420.0Hz