import numpy as np
import time

class ISLRecognizer:
    def __init__(self):
        self.sentence = []
        self.last_sign = None
        self.last_sign_time = time.time()
        self.sign_cooldown = 1.5  # seconds between signs
        
        # ISL Gesture mappings based on finger states
        # Format: (thumb, index, middle, ring, pinky)
        self.gestures = {
            # Letters
            (0,1,0,0,0): "I",
            (1,1,0,0,1): "YOU",
            (0,1,1,0,0): "HELP",
            (1,0,0,0,0): "GOOD",
            (0,0,0,0,0): "NO",
            (1,1,1,1,1): "YES",
            (0,1,1,1,1): "HELLO",
            (1,1,1,0,0): "PLEASE",
            (0,0,1,1,1): "THANK YOU",
            (1,0,0,0,1): "LOVE",
            (0,1,0,1,0): "WATER",
            (1,1,0,0,0): "FOOD",
            (0,0,0,0,1): "SMALL",
            (1,0,1,0,0): "MORE",
            (0,1,0,0,1): "COME",
            (1,0,0,1,0): "GO",
            (0,0,1,0,0): "STOP",
            (1,1,0,1,0): "NAME",
            (0,1,1,1,0): "UNDERSTAND",
            (1,0,1,1,0): "SORRY",
        }

    def recognize_sign(self, finger_states):
        if not finger_states:
            return None
        
        # Convert to tuple for dictionary lookup
        gesture_tuple = tuple(finger_states)
        
        # Check if gesture matches any known sign
        sign = self.gestures.get(gesture_tuple, None)
        return sign

    def update_sentence(self, sign):
        if sign is None:
            return self.sentence
        
        current_time = time.time()
        
        # Only add sign if it's different from last sign
        # or enough time has passed
        if (sign != self.last_sign or 
            current_time - self.last_sign_time > self.sign_cooldown):
            
            if sign != self.last_sign:
                self.sentence.append(sign)
                self.last_sign = sign
                self.last_sign_time = current_time
        
        return self.sentence

    def get_sentence(self):
        return " ".join(self.sentence)

    def clear_sentence(self):
        self.sentence = []
        self.last_sign = None
        return []

    def remove_last_sign(self):
        if self.sentence:
            self.sentence.pop()
            if self.sentence:
                self.last_sign = self.sentence[-1]
            else:
                self.last_sign = None
        return self.sentence