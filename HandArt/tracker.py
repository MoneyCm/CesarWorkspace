import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import os
import numpy as np

class HandTracker:
    def __init__(self, model_path='HandArt/hand_landmarker.task', num_hands=2):
        self.num_hands = num_hands
        
        # Robust path finding
        if not os.path.exists(model_path):
             # Try absolute path based on this file location
             current_dir = os.path.dirname(os.path.abspath(__file__))
             model_path = os.path.join(current_dir, 'hand_landmarker.task')
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}. Please download 'hand_landmarker.task'.")

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=self.num_hands,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.results = None
        self.tip_ids = [4, 8, 12, 16, 20]
        
        # Hand connections (simplified for drawing)
        self.connections = [
            (0,1), (1,2), (2,3), (3,4), # Thumb
            (0,5), (5,6), (6,7), (7,8), # Index
            (0,9), (9,10), (10,11), (11,12), # Middle
            (0,13), (13,14), (14,15), (15,16), # Ring
            (0,17), (17,18), (18,19), (19,20) # Pinky
        ]

    def find_hands(self, img, draw=True):
        # MediaPipe Tasks requires RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)
        
        # Detect
        self.results = self.detector.detect(mp_image)
        
        if draw and self.results.hand_landmarks:
             h, w, c = img.shape
             for hand_lms in self.results.hand_landmarks:
                 # Draw Connections
                 for p1_idx, p2_idx in self.connections:
                     x1 = int(hand_lms[p1_idx].x * w)
                     y1 = int(hand_lms[p1_idx].y * h)
                     x2 = int(hand_lms[p2_idx].x * w)
                     y2 = int(hand_lms[p2_idx].y * h)
                     cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
                     
                 # Draw Landmarks
                 for lm in hand_lms:
                     cx, cy = int(lm.x * w), int(lm.y * h)
                     cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        lm_list = []
        if self.results and self.results.hand_landmarks:
            if hand_no < len(self.results.hand_landmarks):
                my_hand = self.results.hand_landmarks[hand_no]
                h, w, c = img.shape
                for id, lm in enumerate(my_hand):
                     cx, cy = int(lm.x * w), int(lm.y * h)
                     lm_list.append([id, cx, cy])
                     if draw and id == 8: # Index Finger
                         cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
        return lm_list

    def fingers_up(self, lm_list):
        fingers = []
        if len(lm_list) != 0:
            # Thumb (Checking x axis is simplistic and depends on hand side, sticking to user's initial simple logic or refining)
            # Refined: Use x-coordinate comparison relative to Knuckle(2) vs Tip(4) but needs hand handedness.
            # Fallback to simple x < x (Right Hand) logic from original template for now.
            if lm_list[self.tip_ids[0]][1] < lm_list[self.tip_ids[0] - 1][1]: 
                 fingers.append(1)
            else:
                 fingers.append(0)
            
            # 4 Fingers (Tip y < PIP y)
            for id in range(1, 5):
                if lm_list[self.tip_ids[id]][2] < lm_list[self.tip_ids[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers
