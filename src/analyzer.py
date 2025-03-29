import cv2
import mediapipe as mp
import numpy as np
from tkinter import messagebox
import time
import cv2.dnn
import os

mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    refine_landmarks=True
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
        
        self.net = None
        self.classes = []
        self.init_yolo()
        
        self.baseline_eye = None
        self.baseline_head = None
        self.smoothed_probability = 0
        self.time_data = []
        self.eye_tracking_data = []
        self.head_movement_data = []
        self.mouth_movement_data = []
        self.cheating_probability_data = []
        self.mouth_movement_count = 0
        self.ui_callback = None

    def init_yolo(self):
        """Initialize YOLO object detection"""
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            weights_path = os.path.join(script_dir, "yolov4.weights")
            cfg_path = os.path.join(script_dir, "yolov4.cfg")
            names_path = os.path.join(script_dir, "coco.names")
            
            if not all(os.path.exists(path) for path in [weights_path, cfg_path, names_path]):
                print("One or more YOLO files missing")
                return
                
            self.net = cv2.dnn.readNet(weights_path, cfg_path)

            with open(names_path, "r") as f:
                self.classes = [line.strip() for line in f.readlines()]
                
            print("YOLO initialized successfully")
            
        except Exception as e:
            print(f"YOLO initialization failed: {str(e)}")
            self.net = None
            self.classes = []

    def calibrate(self, face_landmarks, shape):
        self.baseline_eye = self.get_eye_tracking(face_landmarks, shape)
        self.baseline_head = self.get_head_movement(face_landmarks, shape)

    def detect_objects(self, frame):
        """Detect prohibited objects with better filtering"""
        if self.net is None:
            return False
            
        prohibited_objects = ["cell phone", "book", "laptop", "paper"]
        
        try:
            blob = cv2.dnn.blobFromImage(frame, 1/255, (416, 416), swapRB=True)
            self.net.setInput(blob)
            outputs = self.net.forward(self.net.getUnconnectedOutLayersNames())
            
            for output in outputs:
                for detection in output:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    
                    if confidence > 0.5 and class_id < len(self.classes):
                        class_name = self.classes[class_id].lower()
                        if any(obj in class_name for obj in prohibited_objects):
                            return True
            return False
        except Exception as e:
            print(f"Object detection error: {str(e)}")
            return False

    def reset_data(self):
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
        self.smoothed_probability = 0

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

            object_detected = False
            if self.net is not None:
                object_detected = self.detect_objects(frame)
                if object_detected:
                    self.log_cheating_event(self.frame_count, "Forbidden object detected")

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = mp_face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    if self.frame_count < 10:
                        self.calibrate(face_landmarks, frame.shape)
                        continue

                    eye_tracking = self.get_eye_tracking(face_landmarks, frame.shape)
                    head_movement = self.get_head_movement(face_landmarks, frame.shape)
                    mouth_movement = self.get_mouth_movement(face_landmarks)
                    gaze_direction = self.get_gaze_direction(face_landmarks)

                    elapsed_time = self.frame_count / self.fps
                    self.time_data.append(elapsed_time)
                    self.eye_tracking_data.append(eye_tracking)
                    self.head_movement_data.append(head_movement)
                    self.mouth_movement_data.append(mouth_movement)

                    if mouth_movement > 5:
                        self.mouth_movement_count += 1

                    cheating_probability = self.calculate_cheating_probability(
                        eye_tracking, 
                        head_movement, 
                        mouth_movement, 
                        is_silent_section=True,
                        object_detected=object_detected
                    )
                    cheating_probability = self.update_smoothed_probability(cheating_probability)
                    self.cheating_probability_data.append(cheating_probability)
                    self.current_probability = cheating_probability

                    if cheating_probability > 60:
                        self.log_cheating_event(self.frame_count, f"High cheating probability: {cheating_probability:.2f}%")
                    if gaze_direction != "CENTER":
                        self.log_cheating_event(self.frame_count, f"Suspicious gaze: {gaze_direction}")
                    
                    self.draw_metrics_on_frame(
                        frame, 
                        eye_tracking, 
                        head_movement, 
                        mouth_movement, 
                        cheating_probability,
                        object_detected=object_detected
                    )
            
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
    
    def draw_metrics_on_frame(self, frame, eye_tracking, head_movement, mouth_movement, cheating_probability, object_detected=False):
        """Draw metrics on the video frame with object detection warning"""
        h, w = frame.shape[:2]
        
        cv2.rectangle(frame, (10, 10), (300, 130), (0, 0, 0), -1)
        cv2.rectangle(frame, (10, 10), (300, 130), (255, 255, 255), 1)

        if object_detected:
            cv2.rectangle(frame, (w-200, 10), (w-10, 50), (0, 0, 255), -1)
            cv2.putText(frame, "OBJECT DETECTED!", (w-190, 35), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
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
        face_width = abs(face_landmarks.landmark[454].x - face_landmarks.landmark[234].x)
        return abs(left_eye.x - right_eye.x) / face_width * 100

    def get_head_movement(self, face_landmarks, shape):
        nose = face_landmarks.landmark[1]
        face_width = abs(face_landmarks.landmark[454].x - face_landmarks.landmark[234].x)
        return abs(nose.x - 0.5) / face_width * 200

    def get_gaze_direction(self, face_landmarks):
        try:
            left_eye_inner = face_landmarks.landmark[33]
            left_eye_outer = face_landmarks.landmark[133]
            right_eye_inner = face_landmarks.landmark[362]
            right_eye_outer = face_landmarks.landmark[263]
            
            left_eye_h = (left_eye_inner.x + left_eye_outer.x) / 2
            right_eye_h = (right_eye_inner.x + right_eye_outer.x) / 2

            gaze_x = (left_eye_h + right_eye_h) / 2
            if gaze_x < 0.4:
                return "LEFT"
            elif gaze_x > 0.6:
                return "RIGHT"
            return "CENTER"
        except (IndexError, AttributeError):
            return "CENTER" 
        
    def get_mouth_movement(self, face_landmarks):
        upper_lip = face_landmarks.landmark[13].y
        lower_lip = face_landmarks.landmark[14].y
        return abs(upper_lip - lower_lip) * 100

    def calculate_cheating_probability(self, eye_tracking, head_movement, mouth_movement, is_silent_section=True, object_detected=False):
        """Calculate cheating probability with object detection penalty"""
        base_weights = {
            'eye': 0.3,
            'head': 0.3,
            'mouth': 0.2,
            'object': 0.2
        }
        
        if object_detected:
            base_weights = {
                'eye': 0.033,
                'head': 0.034,
                'mouth': 0.033,
                'object': 0.9
            }
        
        mouth_weight = 0.3 if is_silent_section else 0.1
        cheating_score = (
            base_weights['eye'] * eye_tracking +
            base_weights['head'] * head_movement +
            base_weights['mouth'] * mouth_movement * mouth_weight
        )
        
        if object_detected:
            cheating_score += base_weights['object'] * 100
        
        return min(100, cheating_score)
    
    def update_smoothed_probability(self, new_probability):
        self.smoothed_probability = 0.9 * self.smoothed_probability + 0.1 * new_probability
        return self.smoothed_probability

    def log_cheating_event(self, frame_num, event_type):
        timestamp = round(frame_num / 30, 2)
        log_msg = f"Time: {timestamp}s - {event_type}\n"
        self.cheating_events.append(log_msg)
        if self.ui_callback:
            self.ui_callback(log_msg)

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
