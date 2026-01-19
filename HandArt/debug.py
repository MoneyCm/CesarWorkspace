import os
import sys

print(f"Python version: {sys.version}")
print(f"Current working dir: {os.getcwd()}")

try:
    import mediapipe as mp
    print("MediaPipe imported.")
    print(f"MediaPipe location: {mp.__file__}")
except ImportError as e:
    print(f"Error importing mediapipe: {e}")
    sys.exit(1)

try:
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    print("MediaPipe Tasks Vision API imported.")
except ImportError as e:
    print(f"Error importing Tasks API: {e}")
    # Inspect what IS available
    import mediapipe.tasks
    print(f"mediapipe.tasks content: {dir(mediapipe.tasks)}")
    sys.exit(1)

model_path = 'HandArt/hand_landmarker.task'
if not os.path.exists(model_path):
    print(f"ERROR: Model file not found at {model_path}")
    # Listing dir
    print(f"Contents of HandArt/: {os.listdir('HandArt')}")
else:
    print(f"Model file found. Size: {os.path.getsize(model_path)} bytes")

print("Attempting to create HandLandmarker...")
try:
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=2
    )
    detector = vision.HandLandmarker.create_from_options(options)
    print("HandLandmarker created successfully!")
except Exception as e:
    print(f"Failed to create HandLandmarker: {e}")
