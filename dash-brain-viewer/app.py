# Created with assistance from ChatGPT (OpenAI)
import os
import json
import time
import threading
import asyncio
import websockets
import numpy as np
import cv2
import base64
import mediapipe as mp
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from mni import create_mesh_data, default_colorscale  # Custom module for brain mesh

# === Gesture Recognition Globals ===
latest_gesture = {"gesture": None, "version": 0}
gesture_event = threading.Event()

COOLDOWN_PERIOD = 0.3
ZOOM_INCREMENT = 0.2
ROTATE_INCREMENT = 0.1
last_swipe_time = 0
last_handled_version = -1

# === MediaPipe Setup ===
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2)
mp_drawing = mp.solutions.drawing_utils

# === Webcam Setup ===
camera = cv2.VideoCapture(0)

def get_frame():
    # Capture a frame from the webcam, process it with MediaPipe to find hand landmarks, draw annotations, overlay current gesture label, and return the image as a base64-encoded JPEG.
    ret, frame = camera.read()
    if not ret:
        return None  
    # Flip horizontally for a mirror view and convert color space for MediaPipe
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    gesture_label = latest_gesture.get("gesture")
    thumb_index_distance = None
    # If any hands are detected, draw landmarks and compute the finger distance
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(255,0,0), thickness=2)
            )

            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            # get the pixel coordinates of the thumb tip and index tip
            h, w, _ = frame.shape
            x1, y1 = int(thumb_tip.x * w), int(thumb_tip.y * h)
            x2, y2 = int(index_tip.x * w), int(index_tip.y * h)
            # compute Euclidean distance between thumb and index finger tips
            thumb_index_distance = int(np.linalg.norm(np.array([x1, y1]) - np.array([x2, y2])))
             # draw a line between thumb and index fingertips and annotate the distance
            cv2.line(frame, (x1, y1), (x2, y2), (255, 255, 0), 2)
            cv2.putText(frame, f"Distance: {thumb_index_distance}px", (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    # overlay the latest recognized gesture on the frame
    if gesture_label:
        cv2.putText(frame, f"Gesture: {gesture_label}", (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 255), 5)
    
    _, buffer = cv2.imencode('.jpg', frame)
    encoded_image = base64.b64encode(buffer).decode('utf-8')
    return f"data:image/jpeg;base64,{encoded_image}"

# === Dash App Setup ===
app = dash.Dash(__name__)
server = app.server
# template for styling the 3D axes in the brain mesh plot
axis_template = {
    "showbackground": True,
    "backgroundcolor": "#141414",
    "gridcolor": "rgb(255, 255, 255)",
    "zerolinecolor": "rgb(255, 255, 255)",
}

# layout configuration for the Plotly 3D brain graph
plot_layout = {
    "title": "",
    "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
    "font": {"size": 12, "color": "white"},
    "showlegend": False,
    "plot_bgcolor": "#141414",
    "paper_bgcolor": "#141414",
    "scene": {
        "xaxis": axis_template,
        "yaxis": axis_template,
        "zaxis": axis_template,
        "aspectratio": {"x": 1, "y": 1.2, "z": 1},
        "camera": {"eye": {"x": 1.25, "y": 1.25, "z": 1.25}},
        "annotations": [],
    },
}
# define the layout of the Dash app
app.layout = html.Div([
    html.Div([
        html.H3("Live Camera Feed with Hand Landmarks", style={'textAlign': 'center', 'color': 'white'}),

        # centered camera feed 
        html.Div([
            html.Img(id='live-camera-feed', style={
                'width': '600px',
                'border': '2px solid white'
            })
        ], style={
            'display': 'flex',
            'justifyContent': 'center',
            'alignItems': 'center',
            'marginBottom': '20px'
        }),

        dcc.Interval(id='interval-camera', interval=100, n_intervals=0),
    ]),

    # 3D brain graph section
    dcc.Graph(
        id="brain-graph",
        figure={"data": create_mesh_data("human_atlas"), "layout": plot_layout},
        config={"editable": True, "scrollZoom": False},
    ),

    dcc.Interval(id="interval-gesture", interval=1000, n_intervals=0),
],
style={'backgroundColor': '#111', 'padding': '20px'}) 


@app.callback(
    Output('live-camera-feed', 'src'),
    Input('interval-camera', 'n_intervals')
)
def update_camera_feed(n):
    #Dash callback to update the live camera feed image every `interval-camera` tick.
    frame = get_frame()
    return frame if frame else dash.no_update

@app.callback(
    Output("brain-graph", "figure"),
    [Input("interval-gesture", "n_intervals")],
    [State("brain-graph", "figure")]
)
def update_camera_on_gesture(n_intervals, figure):
    #Dash callback to modify the 3D brain graph camera view based on the latest gesture. Supports zoom in/out and rotate left/right gestures with cooldown logic.
    global last_swipe_time, last_handled_version
    gesture = latest_gesture.get("gesture")
    version = latest_gesture.get("version")
    current_time = time.time()

    camera_eye = figure["layout"]["scene"]["camera"]["eye"]
    x, y, z = camera_eye["x"], camera_eye["y"], camera_eye["z"]
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)

    if gesture == "zoom_in" and version != last_handled_version and (current_time - last_swipe_time) > COOLDOWN_PERIOD:
        if r > 1.0:
            r -= ZOOM_INCREMENT
            camera_eye["x"] = r * np.cos(theta)
            camera_eye["y"] = r * np.sin(theta)
            print("✅ Gesture handled: zoom_in")
            last_swipe_time = current_time
            last_handled_version = version
            latest_gesture["gesture"] = None

    elif gesture == "zoom_out" and version != last_handled_version and (current_time - last_swipe_time) > COOLDOWN_PERIOD:
        if r < 5.0:
            r += ZOOM_INCREMENT
            camera_eye["x"] = r * np.cos(theta)
            camera_eye["y"] = r * np.sin(theta)
            print("✅ Gesture handled: zoom_out")
            last_swipe_time = current_time
            last_handled_version = version
            latest_gesture["gesture"] = None

    elif gesture == "swipe_left" and version != last_handled_version and (current_time - last_swipe_time) > COOLDOWN_PERIOD:
        theta -= ROTATE_INCREMENT
        camera_eye["x"] = r * np.cos(theta)
        camera_eye["y"] = r * np.sin(theta)
        print("✅ Gesture handled: swipe_left")
        last_swipe_time = current_time
        last_handled_version = version
        latest_gesture["gesture"] = None

    elif gesture == "swipe_right" and version != last_handled_version and (current_time - last_swipe_time) > COOLDOWN_PERIOD:
        theta += ROTATE_INCREMENT
        camera_eye["x"] = r * np.cos(theta)
        camera_eye["y"] = r * np.sin(theta)
        print("✅ Gesture handled: swipe_right")
        last_swipe_time = current_time
        last_handled_version = version
        latest_gesture["gesture"] = None

    figure["layout"]["scene"]["camera"]["eye"] = camera_eye
    return figure

def start_ws_listener():
    #start a new asyncio event loop in a separate thread to listen for gesture messages over WebSocket.
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(gesture_listener())

async def gesture_listener():
    #Connect to the WebSocket server and continuously receive JSON messages indicating gestures.
    # Update `latest_gesture` and signal via `gesture_event` when new data arrives.
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        print("🧪 WebSocket connected!")
        while True:
            try:
                msg = await websocket.recv()
                gesture_data = json.loads(msg)
                print(f"🧠 Received gesture: {gesture_data['gesture']}")
                latest_gesture["gesture"] = gesture_data["gesture"]
                latest_gesture["version"] += 1
                gesture_event.set()
            except websockets.ConnectionClosed:
                print("❌ WebSocket connection closed")
                break

# === Cleanup
import atexit
atexit.register(lambda: camera.release())

if __name__ == "__main__":
    # launch the WebSocket listener in a daemon thread, then start the Dash app
    threading.Thread(target=start_ws_listener, daemon=True).start()
    app.run(debug=True)