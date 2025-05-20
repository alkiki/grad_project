import os
import json
import dash
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.express as px
from mni import create_mesh_data, default_colorscale
from ws_client import latest_gesture, gesture_event  # Import updated gesture data
import threading
import asyncio
import asyncio
import websockets
import json
import threading


app = dash.Dash(__name__)

GITHUB_LINK = os.environ.get(
    "GITHUB_LINK",
    "https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-brain-viewer",
)

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

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Img(src=app.get_asset_url("dash-logo.png")),
                                        html.H4("MRI Reconstruction"),
                                    ],
                                    className="header__title",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Click on the brain to add an annotation. Drag the black corners of the graph to rotate."
                                        )
                                    ],
                                    className="header__info pb-20",
                                ),
                                html.Div(
                                    [
                                        html.A(
                                            "View on GitHub",
                                            href=GITHUB_LINK,
                                            target="_blank",
                                        )
                                    ],
                                    className="header__button",
                                ),
                            ],
                            className="header pb-20",
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id="brain-graph",
                                    figure={
                                        "data": create_mesh_data("human_atlas"),
                                        "layout": plot_layout,
                                    },
                                    config={"editable": True, "scrollZoom": False},
                                )
                            ],
                            className="graph__container",
                        ),
                    ],
                    className="container",
                )
            ],
            className="two-thirds column app__left__section",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P("Select colorscale", className="subheader"),
                        dcc.Dropdown(
                            id="colorscale-picker",
                            options=[
                                {"label": cs, "value": cs}
                                for cs in px.colors.named_colorscales()
                            ],
                            value="Viridis",
                            clearable=False,
                        ),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.P("Select option", className="subheader"),
                        dcc.RadioItems(
                            options=[
                                {"label": "Brain Atlas", "value": "human_atlas"},
                                {"label": "Cortical Thickness", "value": "human"},
                                {"label": "Mouse Brain", "value": "mouse"},
                            ],
                            value="human_atlas",
                            id="radio-options",
                            labelClassName="label__option",
                            inputClassName="input__option",
                        ),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.Span("Click data", className="subheader"),
                        html.Span("  |  "),
                        html.Span("Click on points in the graph.", className="small-text"),
                        dcc.Loading(
                            html.Pre(id="click-data", className="info__container"),
                            type="dot",
                        ),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.Span("Relayout data", className="subheader"),
                        html.Span("  |  "),
                        html.Span(
                            "Drag the graph corners to rotate it.", className="small-text"
                        ),
                        dcc.Loading(
                            html.Pre(id="relayout-data", className="info__container"),
                            type="dot",
                        ),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.Span("Live gesture", className="subheader"),
                        html.Span("  |  "),
                        html.Span("Data received from camera.", className="small-text"),
                        dcc.Loading(
                            html.Pre(id="gesture-data", className="info__container"),
                            type="dot",
                        ),
                    ],
                    className="pb-20",
                ),
                # Add dcc.Store for storing gesture data
                dcc.Store(id="gesture-store", storage_type="memory"),
            ],
            className="one-third column app__right__section",
        ),
        dcc.Interval(id="interval-gesture", interval=1000, n_intervals=0),  # Update every second
        html.Span("Live gesture", className="subheader"),
        dcc.Loading(html.Pre(id="gesture-data", className="info__container"), type="dot"),
    ]
)



import time
import asyncio
import websockets
import json
import threading

COOLDOWN_PERIOD = 1.0
ZOOM_INCREMENT = 0.09
last_swipe_time = 0
last_handled_version = -1  # Track the last gesture version handled
ROTATE_INCREMENT = 0.5  # adjust for faster/slower rotation


# Shared gesture dictionary with version tracking
latest_gesture = {
    "gesture": None,
    "version": 0
}

gesture_event = threading.Event()

# @app.callback(
#     Output("brain-graph", "figure"),
#     [Input("interval-gesture", "n_intervals")],
#     [State("brain-graph", "figure")]
# )
# def update_camera_on_gesture(n_intervals, figure):
#     global last_swipe_time, last_handled_version

#     gesture = latest_gesture.get("gesture")
#     version = latest_gesture.get("version")
#     current_time = time.time()

#     print(f"[Callback] Gesture at {current_time}: {gesture} (v{version})")

#     if (
#         gesture == "zoom_in"
#         and version != last_handled_version
#         and (current_time - last_swipe_time) > COOLDOWN_PERIOD
#     ):
#         camera_eye = figure["layout"]["scene"]["camera"]["eye"]
#         current_x = camera_eye["x"]
#         current_y = camera_eye["y"]

#         if current_x > 1.0:
#             camera_eye["x"] -= ZOOM_INCREMENT
#             camera_eye["y"] -= ZOOM_INCREMENT
#             print("✅ Gesture handled in Dash callback: swipe_right - Zooming in")

#             last_swipe_time = current_time
#             last_handled_version = version  # Mark this version as handled

#             # Reset gesture value, but keep version intact
#             latest_gesture["gesture"] = None

#     return {
#         "data": figure["data"],
#         "layout": figure["layout"],
#     }


def start_ws_listener():
    """Run the WebSocket client in a separate thread"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(gesture_listener())


async def gesture_listener():
    """Listen for gesture data from the WebSocket server"""
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
                print(f"🧠 Updated gesture_data: {latest_gesture}")
                gesture_event.set()
            except websockets.ConnectionClosed:
                print("❌ WebSocket connection closed")
                break


# if __name__ == "__main__":
#     threading.Thread(target=start_ws_listener, daemon=True).start()
#     app.run(debug=True)


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

    print(f"[Callback] Gesture at {current_time}: {gesture} (v{version})")

    if (
        gesture == "zoom_in"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        camera_eye = figure["layout"]["scene"]["camera"]["eye"]
        current_x = camera_eye["x"]
        current_y = camera_eye["y"]

        if current_x > 1.0:
            camera_eye["x"] -= ZOOM_INCREMENT
            camera_eye["y"] -= ZOOM_INCREMENT
            print("✅ Gesture handled in Dash callback: zoom_in - Zooming in")

            last_swipe_time = current_time
            last_handled_version = version  # Mark this version as handled

            # Reset gesture value, but keep version intact
            latest_gesture["gesture"] = None

    elif gesture == "palm":
        # Stop zooming when the palm gesture is detected
        print("✅ Gesture handled in Dash callback: Palm detected - Stopping zoom")
        latest_gesture["gesture"] = None  # Reset the gesture to stop zoom

    elif (
        gesture == "zoom_out"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        camera_eye = figure["layout"]["scene"]["camera"]["eye"]
        current_x = camera_eye["x"]
        current_y = camera_eye["y"]

        if current_x < 5.0:  # Limit zoom-out to avoid going too far
            camera_eye["x"] += ZOOM_INCREMENT
            camera_eye["y"] += ZOOM_INCREMENT
            print("✅ Gesture handled in Dash callback: zoom_out - Zooming out")

            last_swipe_time = current_time
            last_handled_version = version  # Mark this version as handled

            # Reset gesture value, but keep version intact
            latest_gesture["gesture"] = None
    elif (
        gesture == "swipe_left"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        camera_eye = figure["layout"]["scene"]["camera"]["eye"]
        camera_eye["x"] += ROTATE_INCREMENT
        print("✅ Gesture handled: swipe_left - Rotating left")

        last_swipe_time = current_time
        last_handled_version = version
        latest_gesture["gesture"] = None

    elif (
        gesture == "swipe_right"
        and version != last_handled_version
        and (current_time - last_swipe_time) > COOLDOWN_PERIOD
    ):
        camera_eye = figure["layout"]["scene"]["camera"]["eye"]
        camera_eye["x"] -= ROTATE_INCREMENT
        print("✅ Gesture handled: swipe_right - Rotating right")

        last_swipe_time = current_time
        last_handled_version = version
        latest_gesture["gesture"] = None

    return {
        "data": figure["data"],
        "layout": figure["layout"],
    }

if __name__ == "__main__":
    threading.Thread(target=start_ws_listener, daemon=True).start()
    app.run(debug=True)
