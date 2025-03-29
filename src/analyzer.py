import cv2
import mediapipe as mp
import numpy as np
from tkinter import messagebox
import time

mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

FRAME_SKIP = 4  

class VideoAnalyzer:
    def __init__(self):
        self.video_path = None
        self.cheating_events = []
        self.frame_count = 0
        self.final_result = "Pending"
        self.is_analyzing = False
        self.current_frame = None
        self.current_probability = 0
        self.pause_analysis = False
        self.fps = 0

        self.time_data = []
        self.eye_tracking_data = []
        self.head_movement_data = []
        self.mouth_movement_data = []
        self.cheating_probability_data = []
        self.mouth_movement_count = 0

    def reset_data(self):
        """Reset all data for new analysis."""
        self.time_data.clear()
        self.eye_tracking_data.clear()
        self.head_movement_data.clear()
        self.mouth_movement_data.clear()
        self.cheating_probability_data.clear()
        self.mouth_movement_count = 0
        self.cheating_events.clear()
        self.frame_count = 0
        self.final_result = "Pending"
        self.current_probability = 0

    def analyze_video(self, video_path, frame_callback=None, progress_callback=None):
        self.reset_data()
        self.is_analyzing = True

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            messagebox.showerror("Error", "Cannot open video file.")
            self.is_analyzing = False
            return

        self.fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_skip_count = 0

        while cap.isOpened() and self.is_analyzing:
            if self.pause_analysis:
                time.sleep(0.1)
                continue
                
            ret, frame = cap.read()
            if not ret:
                break

            self.frame_count += 1
            frame_skip_count += 1

            if frame_skip_count < FRAME_SKIP:
                continue
            frame_skip_count = 0

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = mp_face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    eye_tracking = self.get_eye_tracking(face_landmarks, frame.shape)
                    head_movement = self.get_head_movement(face_landmarks, frame.shape)
                    mouth_movement = self.get_mouth_movement(face_landmarks)

                    elapsed_time = self.frame_count / self.fps
                    self.time_data.append(elapsed_time)
                    self.eye_tracking_data.append(eye_tracking)
                    self.head_movement_data.append(head_movement)
                    self.mouth_movement_data.append(mouth_movement)

                    if mouth_movement > 5:
                        self.mouth_movement_count += 1

                    cheating_probability = self.calculate_cheating_probability(eye_tracking, head_movement, mouth_movement)
                    self.cheating_probability_data.append(cheating_probability)
                    self.current_probability = cheating_probability

                    if cheating_probability > 60:
                        self.log_cheating_event(self.frame_count, f"Cheating Probability: {cheating_probability:.2f}%")
                    
                    self.draw_metrics_on_frame(frame, eye_tracking, head_movement, mouth_movement, cheating_probability)
            
            self.current_frame = frame
            
            if frame_callback:
                frame_callback(frame)
                
            if progress_callback and total_frames > 0:
                progress = (self.frame_count / total_frames) * 100
                progress_callback(progress)
                
            time.sleep(0.01)

        cap.release()
        self.generate_final_result()
        self.is_analyzing = False

    def draw_metrics_on_frame(self, frame, eye_tracking, head_movement, mouth_movement, cheating_probability):
        """Draw metrics on the video frame."""
        h, w = frame.shape[:2]
        cv2.rectangle(frame, (10, 10), (300, 130), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, 130), (255, 255, 255), 1)
        cv2.putText(frame, f"Eye Movement: {eye_tracking:.1f}", (20, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1)
        cv2.putText(frame, f"Head Movement: {head_movement:.1f}", (20, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        cv2.putText(frame, f"Mouth Movement: {mouth_movement:.1f}", (20, 85), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)
        color = (0, 255, 0)
        if cheating_probability > 60:
            color = (0, 0, 255)
        elif cheating_probability > 30:
            color = (0, 165, 255)
        cv2.putText(frame, f"Cheating Probability: {cheating_probability:.1f}%", (20, 110), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        if self.mouth_movement_count > 0:
            cv2.putText(frame, f"Talking Events: {self.mouth_movement_count}", 
                        (w - 200, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

    def get_eye_tracking(self, face_landmarks, shape):
        left_eye = face_landmarks.landmark[33]
        right_eye = face_landmarks.landmark[263]
        return abs(left_eye.x - right_eye.x) * 100

    def get_head_movement(self, face_landmarks, shape):
        nose = face_landmarks.landmark[1]
        return abs(nose.x - 0.5) * 200

    def get_mouth_movement(self, face_landmarks):
        upper_lip = face_landmarks.landmark[13].y
        lower_lip = face_landmarks.landmark[14].y
        return abs(upper_lip - lower_lip) * 100

    def calculate_cheating_probability(self, eye_tracking, head_movement, mouth_movement):
        cheating_score = (0.4 * eye_tracking) + (0.4 * head_movement) + (0.2 * mouth_movement)
        return min(100, cheating_score)

    def log_cheating_event(self, frame_num, event_type):
        timestamp = round(frame_num / 30, 2)
        self.cheating_events.append(f"Time: {timestamp}s - {event_type}")

    def generate_final_result(self):
        if len(self.cheating_probability_data) == 0:
            self.final_result = "No data available"
            return
        if self.mouth_movement_count > 5:
            self.final_result = "Rejected (Excessive Talking)"
            return
        avg_cheating_probability = sum(self.cheating_probability_data) / len(self.cheating_probability_data)
        if avg_cheating_probability > 50:
            self.final_result = "Rejected (Suspicious Behavior)"
        else:
            self.final_result = "Selected (No Suspicious Behavior)"