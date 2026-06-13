import cv2
import mediapipe as mp
import numpy as np

class FaceTracker:
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.drawing_spec = self.mp_draw.DrawingSpec(
            thickness=1, 
            circle_radius=1
        )

    def find_face(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        landmarks_list = []

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Draw face mesh on frame
                self.mp_draw.draw_landmarks(
                    image=frame,
                    landmark_list=face_landmarks,
                    connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                    landmark_drawing_spec=self.drawing_spec,
                    connection_drawing_spec=self.drawing_spec
                )
                # Extract landmarks
                landmarks = []
                for lm in face_landmarks.landmark:
                    landmarks.append([lm.x, lm.y, lm.z])
                landmarks_list.append(landmarks)

        return frame, landmarks_list

    def detect_emotion(self, landmarks):
        if not landmarks:
            return "neutral"

        face = landmarks[0]

        # Key landmark points
        left_eyebrow = face[70]
        right_eyebrow = face[300]
        left_eye_top = face[159]
        left_eye_bottom = face[145]
        right_eye_top = face[386]
        right_eye_bottom = face[374]
        mouth_left = face[61]
        mouth_right = face[291]
        mouth_top = face[13]
        mouth_bottom = face[14]
        nose_tip = face[4]
        left_cheek = face[234]
        right_cheek = face[454]

        # Measurements
        face_height = abs(face[10][1] - face[152][1])
        if face_height == 0:
            return "neutral"

        # Normalize all measurements by face height
        mouth_open = abs(mouth_top[1] - mouth_bottom[1]) / face_height
        mouth_width = abs(mouth_left[0] - mouth_right[0]) / face_height
        left_eye_open = abs(left_eye_top[1] - left_eye_bottom[1]) / face_height
        right_eye_open = abs(right_eye_top[1] - right_eye_bottom[1]) / face_height
        avg_eye_open = (left_eye_open + right_eye_open) / 2
        left_brow_height = abs(left_eyebrow[1] - left_eye_top[1]) / face_height
        right_brow_height = abs(right_eyebrow[1] - right_eye_top[1]) / face_height
        avg_brow_height = (left_brow_height + right_brow_height) / 2

        # Mouth corners for smile detection
        mouth_corner_avg = (mouth_left[1] + mouth_right[1]) / 2
        mouth_center = mouth_top[1]
        smile_score = (mouth_corner_avg - mouth_center) / face_height

        # Emotion detection with normalized values
        # Surprised — wide eyes + raised brows + open mouth
        if avg_eye_open > 0.045 and avg_brow_height > 0.08 and mouth_open > 0.03:
            return "surprised"

        # Happy — smile (mouth corners up) + open mouth
        elif smile_score < -0.01 and mouth_width > 0.12:
            return "happy"

        # Angry — low brows + narrow eyes
        elif avg_brow_height < 0.04 and avg_eye_open < 0.025:
            return "angry"

        # Disgusted — low brows + one side raised + mouth closed
        elif avg_brow_height < 0.05 and mouth_open < 0.02:
            return "disgusted"

        # Sad — drooping mouth corners + slightly closed eyes
        elif smile_score > 0.015 and avg_eye_open < 0.03:
            return "sad"

        else:
            return "neutral"