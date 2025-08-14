# 🏋️‍♂️ Push-Up Tracker using Python, OpenCV & MediaPipe

A real-time push-up counter powered by computer vision — no sensors, no wearables, just your webcam and smart pose estimation.

## 🛠️ Tech Stack

- **Python**
- **OpenCV**
- **MediaPipe**
- **NumPy**

## 🚀 How It Works

1. Captures webcam feed using OpenCV
2. Uses MediaPipe Pose to detect key landmarks
3. Calculates elbow angle to determine push-up motion
4. Counts reps and displays feedback in real time
5. Dual Arm Tracking Tracks both left & right elbow angles. Push-up is counted only if both arms are in correct range (down < 90°, up > 160°).Prevents cheating with one-arm half reps.
6. Calories Burned EstimationAs you do push-ups, it shows estimated calories burned.
Formula: Calories = MET (8) × weight(kg) × time(hours).
Your weight can be set at the start of the script.
7. Push-Up Speed Tracker Measures time taken for each push-up.Displays average push-up speed on screen.Shows warning "Too Fast! Slow Down!" if a push-up is under 0.5 seconds.
8. Session Timer Shows how long your push-up session has been running in MM:SS format.
9. Form Detection Warning If your elbow angle range is too small (e.g., not going low enough), shows "Incomplete Push-up" warning.
10. Achievement Messages Shows motivational popups when you hit milestones:
🔥 Keep Going! at 10 push-ups
💪 Strong! at 20 push-ups
🏆 Champion! at 50 push-ups
11. Data Logging to CSV Automatically saves your push-up data to pushup_log.csv after each session:
Date & Time
Total Push-ups
Total Calories Burned
Average Speed
Session Duration



cd pushup-tracker
pip install -r requirements.txt
python pushup_tracker.py
