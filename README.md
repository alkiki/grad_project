# grad_project
This project currently runs with 2 different environemtns. 

Clone the repository

`git clone https://github.com/alkiki/grad_project.git
cd grad_project`

For the Camera + Gesture Script
`# Create and activate a virtual environment
python3 -m venv camenv
source camenv/bin/activate  # Use camenv\Scripts\activate on Windows
# Install required packages
pip install --upgrade pip
pip install -r requirements_camera.txt`

For the Server + Dash Visualization:

`# Create and activate Conda environment
conda env create -f environment_camera.yml
conda activate dashenv`


Run the project
Terminal 1: Dash App & WebSocket Server
`conda activate dashenv
# Run the server
python websocket_server.py

# In another terminal (still in dashenv)
python dash-brain-viewer/app.py`

Terminal 2: Camera Script
`source camenv/bin/activate
python camera.py`
