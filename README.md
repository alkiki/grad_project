# 🎓 grad_project

WORKING ENVIRONMENTS: CCI_UG_thesis/camenv.yml and CCI_UG_thesis/mediapipe_env.yml

This project uses webcam-based hand gesture recognition to interact with a Dash-based 3D visualization via WebSockets.

It runs in **two environments**:
- 🖐️ `venv` for the camera + gesture model
- 📊 `conda` for the server + visualization

---

## Quick Setup & Run Instructions

###  1. Clone the repository

```bash
git clone https://github.com/alkiki/grad_project.git
cd grad_project
```
### 2. Set up the camera gesture environment (venv)
```
# Create and activate the Conda environment
conda env create -f mediapipe_env.yml
conda activate mediapipe_env
```
### 3. Set up the Dash + WebSocket environment (conda)
```# Create and activate the Conda environment
conda env create -f camenv.yml
conda activate camenv
```
### 4. Run the project (in two terminals)
#### Terminal 1: WebSocket server and Dash app
```conda activate dashenv
python websocket_server.py
```
#### Open a second tab (same environment):
```conda activate dashenv
python dash-brain-viewer/app.py
```
Then open your browser to:
http://127.0.0.1:8050

#### Terminal 2: Run the camera script
```source camenv/bin/activate           # On Windows: camenv\Scripts\activate
python camera.py
```

