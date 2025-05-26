# Created with assistance from ChatGPT (OpenAI)
import cv2
import numpy as np
import mediapipe as mp
from collections import deque
from tensorflow.keras.models import load_model
import time
import asyncio
import websockets
import json
import math

# Orientation Feature Utilities 
def unit_vector(v):
    #  Normalize a vector to unit length. Return zero vector if input has zero length.
    norm = np.linalg.norm(v)
    return v / norm if norm != 0 else v

def compute_orientation_features(lm_array):
    # Compute orientation features from landmark array:
    # - wrist_to_middle: direction from wrist to middle finger MCP
    #- index_to_pinky: direction from index MCP to pinky MCP
    #- palm_normal: normal vector of the palm plane
    lm = np.array(lm_array).reshape(-1, 3)
    WRIST, INDEX_MCP, PINKY_MCP, MIDDLE_MCP = 0, 5, 17, 9
    #  Vector from wrist to middle MCP (finger base)
    wrist_to_middle = unit_vector(lm[MIDDLE_MCP] - lm[WRIST])
    # Vector across palm between index MCP and pinky MCP
    index_to_pinky = unit_vector(lm[PINKY_MCP] - lm[INDEX_MCP])
    # Compute palm normal via cross product of two palm vectors
    v1 = lm[INDEX_MCP] - lm[WRIST]
    v2 = lm[PINKY_MCP] - lm[WRIST]
    palm_normal = unit_vector(np.cross(v1, v2))
    # Concatenate all three feature vectors
    return np.concatenate([wrist_to_middle, index_to_pinky, palm_normal])

async def send_gesture(gesture):
    #Asynchronously send a JSON-encoded gesture message to the WebSocket server.
    uri = "ws://localhost:8765"
    try:
        message = json.dumps({"gesture": gesture})
        async with websockets.connect(uri) as websocket:
            await websocket.send(message)
            print(f"📨 Gesture sent: {message}")
    except Exception as e:
        print(f"[WebSocket Error] {e}")

# Load LSTM model 
model = load_model("/Users/azatagafarov/Desktop/website_gesture_model/gesture recognition model/model_lstm_swiping_best_verison.keras")
class_names = ["fist", "grabbing", "left_palm", "palm", "point", "rigth_palm_", "stop_inverted_cropped", "swipe_left", "swipe_right", "three2", "thumb_index", "two_up"]

# MediaPipe setup 
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# === Buffers & Constants ===
SEQUENCE_LENGTH = 5
landmark_buffer = deque(maxlen=SEQUENCE_LENGTH)
gesture_history = deque(maxlen=2)
zoom_mode_triggered = False
last_zoom_time = 0
ZOOM_COOLDOWN = 1.0
last_dynamic_time = 0
DETECTION_COOLDOWN = 1.5  # seconds

cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Mirror image for user-friendly display and convert to RGB for MediaPipe
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape
     # Process frame for hand landmarks
    results = hands.process(rgb)

    dist = None
    # If at least one hand is detected  
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Draw landmarks and connections on the frame
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            # Flatten landmark coordinates into a single list
            landmarks = [coord for lm in hand_landmarks.landmark for coord in (lm.x, lm.y, lm.z)]
            orientation = compute_orientation_features(landmarks)
            enhanced = landmarks + orientation.tolist()
            landmark_buffer.append(enhanced)

            # # Calculate normalized distance between thumb tip and index tip for pinch zoom
            thumb_tip = hand_landmarks.landmark[4]
            index_tip = hand_landmarks.landmark[8]
            dist = math.sqrt((thumb_tip.x - index_tip.x) ** 2 + (thumb_tip.y - index_tip.y) ** 2)
            # Draw line between thumb and index and display pixel distance
            cv2.line(frame, (int(thumb_tip.x * w), int(thumb_tip.y * h)),
                     (int(index_tip.x * w), int(index_tip.y * h)), (0, 255, 255), 2)
            cv2.putText(frame, f"Distance: {dist:.2f}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
        # Once we have enough frames, run the LSTM model
        if len(landmark_buffer) == SEQUENCE_LENGTH:
            input_seq = np.array(landmark_buffer).reshape(1, SEQUENCE_LENGTH, 72)
            prediction = model.predict(input_seq, verbose=0)
            predicted_label = class_names[np.argmax(prediction)]
            # Display predicted label on frame
            cv2.putText(frame, predicted_label, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

             # === Mode Switching: Palm stops zoom, Fist starts zoom ===
            if not gesture_history or gesture_history[-1] != predicted_label:
                gesture_history.append(predicted_label)

            if predicted_label == "palm":
                zoom_mode_triggered = False
                landmark_buffer.clear()
                cv2.putText(frame, "🛑 Zoom mode OFF", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
                print("✋ Palm detected – stopping gesture recognition mode.")

            elif predicted_label == "fist":
                zoom_mode_triggered = True
                cv2.putText(frame, "✅ Zoom mode ON", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                print("✊ Fist detected – zoom mode activated.")

            # Zoom gesture logic
            if zoom_mode_triggered and dist is not None:
                current_time = time.time()
                if current_time - last_zoom_time > ZOOM_COOLDOWN:
                    if dist > 0.13:
                        print("👐 Detected zoom_in by pinch")
                        cv2.putText(frame, "zoom_in", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 100, 100), 2)
                        asyncio.run(send_gesture("zoom_in"))
                        last_zoom_time = current_time
                    elif dist < 0.13:
                        print("🤏 Detected zoom_out by pinch")
                        cv2.putText(frame, "zoom_out", (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
                        asyncio.run(send_gesture("zoom_out"))
                        last_zoom_time = current_time

            # Dynamic gesture matching
            if len(gesture_history) == 2:
                recent = list(gesture_history)
                for name, pattern in {
                    "swipe_left": ["point", "swipe_left"],
                    "swipe_right": ["point", "swipe_right"],
                    # "rotate_cw": ["palm", "thumb_index"],
                    # "rotate_ccw": ["thumb_index", "palm"]
                }.items():
                    if recent == pattern and (time.time() - last_dynamic_time) > DETECTION_COOLDOWN:
                        print(f"🔁 Detected dynamic gesture: {name}")
                        cv2.putText(frame, name, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 200, 255), 2)
                        last_dynamic_time = time.time()
                        asyncio.run(send_gesture(name))
                        gesture_history.clear()



    cv2.imshow("LSTM Dynamic Gesture + Pinch Zoom", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
hands.close()