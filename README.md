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

<img width="200" alt="Screenshot 2025-05-26 at 6 44 06 AM" src="https://github.com/user-attachments/assets/217fd1e7-b901-4618-8906-8ccc5a7f5494" />
<img width="200" alt="Screenshot 2025-05-26 at 6 45 01 AM" src="https://github.com/user-attachments/assets/5f5e5dd2-ef57-4a67-9981-73c63331c31a" />


"Swiping gesture"
<img width="200" alt="Screenshot 2025-05-26 at 6 49 21 AM" src="https://github.com/user-attachments/assets/f39d4636-5957-4680-8cdd-f364c1383887" />
<img width="200" alt="Screenshot 2025-05-26 at 6 46 37 AM" src="https://github.com/user-attachments/assets/e82b3ae0-b7aa-4f16-926a-f01297557de0" />
<img width="200" alt="Screenshot 2025-05-26 at 6 53 49 AM" src="https://github.com/user-attachments/assets/611e1da1-f7e2-42cc-8e0a-2518e1ccbad2" />
<img width="200" alt="Screenshot 2025-05-26 at 6 56 15 AM" src="https://github.com/user-attachments/assets/1374c39c-1e62-4668-b28b-ed40dd0da3b4" />
<img width="200" alt="Screenshot 2025-05-26 at 6 57 45 AM" src="https://github.com/user-attachments/assets/0e9b27c1-45af-401e-9356-9f6e2551ba8b" />


"Fist" to activate the zoom mode 
<img width="200" alt="Screenshot 2025-05-26 at 6 43 17 AM" src="https://github.com/user-attachments/assets/dd445ea8-30b6-4bea-9f5d-653672f9ac16" />


Open "palm" gesture
<img width="200" alt="Screenshot 2025-05-26 at 6 43 43 AM" src="https://github.com/user-attachments/assets/df47d849-2e97-46ea-8e43-1f895f101a18" />
