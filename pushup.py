import cv2
import mediapipe as mp
import numpy as np
import math
import time
import csv
from datetime import datetime
import os
import winsound  # For Windows sound notifications

# ===========================
# CONFIGURATION
# ===========================
USER_WEIGHT_KG = 70  # Set your weight for calorie calculation
PUSHUP_MET = 8       # MET for push-ups
CSV_FILE = "pushup_log.csv"

# Create CSV file if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Push-ups", "Calories", "Session_Time"])

# ===========================
# SETUP
# ===========================
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

# ===========================
# VARIABLES
# ===========================
counter = 0
stage = None
start_time = time.time()
pushup_times = []
achievement_flags = set()

# ===========================
# VIDEO CAPTURE
# ===========================
cap = cv2.VideoCapture(0)

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width, _ = frame.shape

        # ===========================
        # ATTRACTIVE BACKGROUND
        # ===========================
        overlay = np.zeros_like(frame, dtype=np.uint8)
        overlay[:] = (20, 20, 40)  # dark blue-ish background
        alpha = 0.4
        frame = cv2.addWeighted(overlay, alpha, frame, 1-alpha, 0)

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = pose.process(image)
        image.flags.writeable = True
        frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # ===========================
        # HEADER BAR
        # ===========================
        cv2.rectangle(frame, (0,0), (width,100), (50,50,70), -1)
        cv2.putText(frame, "PowerPush AI Pro", (width//2 - 250, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (0,255,0), 3)

        try:
            landmarks = results.pose_landmarks.landmark

            # LEFT ARM
            left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * width,
                             landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * height]
            left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * width,
                          landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * height]
            left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x * width,
                          landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y * height]
            left_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)

            # RIGHT ARM
            right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * width,
                              landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * height]
            right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x * width,
                           landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y * height]
            right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * width,
                           landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * height]
            right_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

            # ===========================
            # DISPLAY ANGLES
            # ===========================
            cv2.putText(frame, f'Left Elbow: {int(left_angle)}°', (30,70), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255,255,0),2)
            cv2.putText(frame, f'Right Elbow: {int(right_angle)}°', (30,100), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255,255,0),2)

            # ===========================
            # PUSH-UP COUNT
            # ===========================
            min_angle = 90
            max_angle = 160

            if left_angle > max_angle and right_angle > max_angle:
                stage = "up"
            if left_angle < min_angle and right_angle < min_angle and stage == "up":
                stage = "down"
                counter +=1
                pushup_times.append(time.time())

                # ===========================
                # CSV LOGGING
                # ===========================
                elapsed_hours = (time.time() - start_time)/3600
                calories = PUSHUP_MET * USER_WEIGHT_KG * elapsed_hours
                session_time = int(time.time() - start_time)
                with open(CSV_FILE, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), counter, round(calories,2), session_time])

            # Form warning
            if left_angle > min_angle + 10 and left_angle < min_angle + 40:
                cv2.putText(frame, "Incomplete Push-up!", (width//2 - 180, height - 50), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0,0,255),3)

            # ===========================
            # SPEED
            # ===========================
            avg_speed = 0
            if len(pushup_times) > 1:
                intervals = [pushup_times[i+1]-pushup_times[i] for i in range(len(pushup_times)-1)]
                avg_speed = sum(intervals)/len(intervals)
                if intervals[-1] < 0.5:
                    cv2.putText(frame, "Too Fast! Slow Down!", (width//2 - 200, height - 80), cv2.FONT_HERSHEY_DUPLEX, 1, (0,0,255),2)

            # ===========================
            # CALORIES
            # ===========================
            elapsed_hours = (time.time() - start_time)/3600
            calories = PUSHUP_MET * USER_WEIGHT_KG * elapsed_hours

            # ===========================
            # SESSION TIMER
            # ===========================
            elapsed_time = int(time.time() - start_time)
            mins = elapsed_time//60
            secs = elapsed_time%60
            timer_text = f"{mins:02d}:{secs:02d}"

            # ===========================
            # ACHIEVEMENTS + SOUND
            # ===========================
            milestones = {10:"🔥 Keep Going!", 20:"💪 Strong!", 50:"🏆 Champion!"}
            if counter in milestones and counter not in achievement_flags:
                achievement_flags.add(counter)
                cv2.putText(frame, milestones[counter], (width//2 - 200, height//2), cv2.FONT_HERSHEY_DUPLEX, 2, (0,255,255),3)
                winsound.Beep(1000, 300)  # Sound notification

            # ===========================
            # DISPLAY INFO
            # ===========================
            cv2.putText(frame, f'Push-ups: {counter}', (width//2 - 150, 140), cv2.FONT_HERSHEY_DUPLEX, 2, (0,255,255),3)
            cv2.putText(frame, f'Calories: {int(calories)} kcal', (width//2 - 150,180), cv2.FONT_HERSHEY_DUPLEX,1.2,(255,255,0),2)
            cv2.putText(frame, f'Avg Speed: {avg_speed:.2f}s', (width//2 - 150,210), cv2.FONT_HERSHEY_DUPLEX,1.2,(255,255,0),2)
            cv2.putText(frame, f'Timer: {timer_text}', (width//2 - 150,240), cv2.FONT_HERSHEY_DUPLEX,1.2,(0,255,0),2)

            # ===========================
            # PROGRESS BARS (GRADIENT)
            # ===========================
            bar_left = np.interp(left_angle,(90,160),(350,0))
            bar_right = np.interp(right_angle,(90,160),(350,0))
            for i in range(int(350-bar_left),350):
                color = (0,int(255*(i-(350-bar_left))/bar_left),255-int(255*(i-(350-bar_left))/bar_left))
                cv2.line(frame,(100,i+150),(150,i+150),color,2)
                cv2.line(frame,(width-150,i+150),(width-100,i+150),color,2)
            cv2.rectangle(frame,(100,150),(150,500),(255,255,255),2)
            cv2.rectangle(frame,(width-150,150),(width-100,500),(255,255,255),2)
            cv2.circle(frame,(125,150),10,(255,0,255),-1)
            cv2.circle(frame,(width-125,150),10,(255,0,255),-1)

            # Draw landmarks
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                      mp_drawing.DrawingSpec(color=(0,255,255),thickness=6,circle_radius=8),
                                      mp_drawing.DrawingSpec(color=(255,0,255),thickness=4,circle_radius=6))
        except:
            pass

        # ===========================
        # SHOW FRAME
        # ===========================
        cv2.imshow('PowerPush AI Pro', frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
