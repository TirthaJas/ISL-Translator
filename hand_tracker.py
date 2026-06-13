import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.mp_draw = mp.solutions.drawing_utils

    def find_hands(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        landmarks_list = []

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on frame
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                # Extract landmark positions
                landmarks = []
                for lm in hand_landmarks.landmark:
                    landmarks.append([lm.x, lm.y, lm.z])
                landmarks_list.append(landmarks)

        return frame, landmarks_list

    def get_finger_states(self, landmarks):
        if not landmarks:
            return None
        
        fingers = []
        # Thumb
        fingers.append(1 if landmarks[4][0] < landmarks[3][0] else 0)
        # Other 4 fingers
        for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
            fingers.append(1 if landmarks[tip][1] < landmarks[pip][1] else 0)
        
        return fingers