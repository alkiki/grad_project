import os
import json
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.express as px
from mni import create_mesh_data, default_colorscale
import threading
import asyncio
import websockets
import time
import numpy as np

# Shared gesture dictionary
latest_gesture = {"gesture": None, "version": 0}
gesture_event = threading.Event()

# Constants
COOLDOWN_PERIOD = 0.3
ZOOM_INCREMENT = 0.2
ROTATE_INCREMENT = 0.1
last_swipe_time = 0
last_handled_version = -1

app = dash.Dash(__name__)

axis_template = {
    "showbackground": True,
    "backgroundcolor": "#141414",
    "gridcolor": "rgb(255, 255, 255)",
    "zerolinecolor": "rgb(255, 255, 255)",
}

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

app.layout = html.Div([
    dcc.Graph(
        id="brain-graph",
        figure={"data": create_mesh_data("human_atlas"), "layout": plot_layout},
        config={"editable": True, "scrollZoom": False},
    ),
    dcc.Interval(id="interval-gesture", interval=1000, n_intervals=0),
])

@app.callback(
    Output("brain-graph", "figure"),
    [Input("interval-gesture", "n_intervals")],
    [State("brain-graph", "figure")]
)
def update_camera_on_gesture(n_intervals, figure):
    global last_swipe_time, last_handled_version

    gesture = latest_gesture.get("gesture")
    version = latest_gesture.get("version")
    current_time = time.time()

    camera_eye = figure["layout"]["scene"]["camera"]["eye"]
    x, y, z = camera_eye["x"], camera_eye["y"], camera_eye["z"]
    r = np.sqrt(x**2 + y**2)
    theta = np.arctan2(y, x)

    if (
        gesture == "zoom_in"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        if r > 1.0:
            r -= ZOOM_INCREMENT
            camera_eye["x"] = r * np.cos(theta)
            camera_eye["y"] = r * np.sin(theta)
            print("✅ Gesture handled: zoom_in - Zooming in")

            last_swipe_time = current_time
            last_handled_version = version
            latest_gesture["gesture"] = None

    elif (
        gesture == "zoom_out"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        if r < 5.0:
            r += ZOOM_INCREMENT
            camera_eye["x"] = r * np.cos(theta)
            camera_eye["y"] = r * np.sin(theta)
            print("✅ Gesture handled: zoom_out - Zooming out")

            last_swipe_time = current_time
            last_handled_version = version
            latest_gesture["gesture"] = None

    elif (
        gesture == "swipe_left"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        theta -= ROTATE_INCREMENT
        camera_eye["x"] = r * np.cos(theta)
        camera_eye["y"] = r * np.sin(theta)
        print("✅ Gesture handled: swipe_left - Rotating left")

        last_swipe_time = current_time
        last_handled_version = version
        latest_gesture["gesture"] = None

    elif (
        gesture == "swipe_right"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        theta += ROTATE_INCREMENT
        camera_eye["x"] = r * np.cos(theta)
        camera_eye["y"] = r * np.sin(theta)
        print("✅ Gesture handled: swipe_right - Rotating right")

        last_swipe_time = current_time
        last_handled_version = version
        latest_gesture["gesture"] = None

    # Update camera
    figure["layout"]["scene"]["camera"]["eye"] = camera_eye
    return figure


def start_ws_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(gesture_listener())


async def gesture_listener():
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


if __name__ == "__main__":
    threading.Thread(target=start_ws_listener, daemon=True).start()
    app.run(debug=True)
