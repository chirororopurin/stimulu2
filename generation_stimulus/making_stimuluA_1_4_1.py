import cv2
import mediapipe as mp
import numpy as np
from pydub import AudioSegment
import ffmpeg
import os

# --- 設定 ---
sound_file = "gou1.wav"         # 元音声
input_video = "A_sample.mp4"    # 入力動画
temp_video = "temp_video.mp4"
temp_audio = "temp_audio.wav"
final_video = "output_with_volume_distanceA.mp4"

# --- 音声読み込み ---
base_sound = AudioSegment.from_file(sound_file)

# 元音声を少し下げる（クリップ防止）
base_sound = base_sound   # -12dB

# --- MediaPipe初期化 ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# --- 動画読み込み ---
cap = cv2.VideoCapture(input_video)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))

# --- 距離判定パラメータ ---
distance_threshold = 0.10  # 音量アップ開始距離
max_distance = 0.165       # 音量最大距離
max_boost_db = 100          # 音量最大増幅(dB)
boost_duration_ms = 100   # フェード時間(ms)

# --- 音量アップタイム記録 ---
boost_times = []

print("🎬 動画処理開始…")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 映像上下反転
    frame = cv2.flip(frame, 0)

    # MediaPipe処理
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image.flags.writeable = False
    results = pose.process(image)
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    current_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000

    # --- 音量判定 ---
    frame_boost_db = 0.0
    if results.pose_landmarks:
        for side in ["RIGHT", "LEFT"]:
            wrist_id = mp_pose.PoseLandmark.RIGHT_WRIST if side == "RIGHT" else mp_pose.PoseLandmark.LEFT_WRIST
            shoulder_id = mp_pose.PoseLandmark.RIGHT_SHOULDER if side == "RIGHT" else mp_pose.PoseLandmark.LEFT_SHOULDER

            wrist = results.pose_landmarks.landmark[wrist_id]
            shoulder = results.pose_landmarks.landmark[shoulder_id]

            # 手首と肩の距離
            dist = np.sqrt((wrist.x - shoulder.x)**2 + (wrist.y - shoulder.y)**2)

            if dist > distance_threshold:
                vol_ratio = min((dist - distance_threshold) / (max_distance - distance_threshold), 1.0)
                frame_boost_db = max(frame_boost_db, vol_ratio * max_boost_db)

    if frame_boost_db > 0:
        start_ms = int(current_time * 1000)
        end_ms = start_ms + boost_duration_ms
        boost_times.append((start_ms, end_ms, frame_boost_db))
        print(f"🔊 音量アップ: {current_time:.2f}s / {frame_boost_db:.1f} dB")

    # --- 動画書き出し ---
    out.write(image)

    # プレビュー
    cv2.imshow("Motion Volume Boost", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# --- 後処理 ---
cap.release()
out.release()
cv2.destroyAllWindows()
pose.close()

print("📄 一時動画作成完了:", temp_video)

# --- 音声合成 ---
# 動画長さに合わせて元音声をループ
cap = cv2.VideoCapture(input_video)
video_duration_ms = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / fps * 1000)
cap.release()
audio_track = base_sound
audio_track = audio_track[:video_duration_ms]

# --- 音量ブースト処理 ---
for start_ms, end_ms, boost_db in boost_times:
    segment = audio_track[start_ms:end_ms] + boost_db
    segment = segment.fade_in(boost_duration_ms).fade_out(boost_duration_ms)
    audio_track = audio_track[:start_ms] + segment + audio_track[end_ms:]

# --- 音声書き出し ---
audio_track.export(temp_audio, format="wav")

# --- 映像 + 音声マージ ---
ffmpeg.input(temp_video).output(
    ffmpeg.input(temp_audio),
    final_video,
    vcodec="copy",
    acodec="aac",
    strict="experimental"
).run(overwrite_output=True)

print("🎉 出力完了:", final_video)

# 一時ファイル削除
os.remove(temp_video)
os.remove(temp_audio)
