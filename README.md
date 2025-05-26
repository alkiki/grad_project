# 🎓 grad_project

WORKING ENVIRONMENTS: CCI_UG_thesis/camenv.yml and CCI_UG_thesis/mediapipe_env.yml

This project uses webcam-based hand gesture recognition to interact with a Dash-based 3D visualization via WebSockets.
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
```conda activate mediapipe_env
python gesture_recognition_model/websocket_server.py
```
#### Open a second tab (same environment):
```conda activate camenv
python dash-brain-viewer/app.py
```
Then open your browser to:
http://127.0.0.1:8050

#### Terminal 2: Run the camera script
```conda activate mediapipe_env       # On Windows: camenv\Scripts\activate
python gesture_recognition_model/lstm_model_camera.py
```
Instruction on how to interact with project. 
"Zoom in gesture"
The zoom mode is triggered only after the "fist" gesture. The zoom mode stops after the "palm" gesture


<img width="137" alt="Screenshot 2025-05-26 at 5 04 21 AM" src="https://github.com/user-attachments/assets/d3700ef7-be78-47df-80c7-d663dd57e0e8" />


"Swiping gesture"


<img width="91" alt="Screenshot 2025-05-26 at 5 09 04 AM" src="https://github.com/user-attachments/assets/9f0bea2a-3042-4407-9bf2-0be161ee0caa" />
<img width="93" alt="Screenshot 2025-05-26 at 5 11 46 AM" src="https://github.com/user-attachments/assets/f788df7b-ebac-4c15-8461-3616c53444e4" />


"Fist" to activate the zoom mode 


<img width="146" alt="Screenshot 2025-05-26 at 5 14 02 AM" src="https://github.com/user-attachments/assets/367d8f8a-9d40-4ec1-9075-189a24421f54" />


Open "palm" gesture


<img width="146" alt="Screenshot 2025-05-26 at 5 14 56 AM" src="https://github.com/user-attachments/assets/5ba655cc-3f25-44a3-b715-16fbf650f2e8" />
