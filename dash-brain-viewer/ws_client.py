
# import asyncio
# import websockets
# import json
# import threading

# latest_gesture = {"gesture": None}
# gesture_event = threading.Event()

# async def send_gesture(gesture):
#     uri = "ws://localhost:8765"
#     try:
#         async with websockets.connect(uri) as websocket:
#             message = json.dumps({"gesture": gesture})
#             await websocket.send(message)
#             print(f"📨 Gesture sent: {message}")
#     except Exception as e:
#         print(f"[WebSocket Error] {e}")

# async def listen_for_gestures():
#     uri = "ws://localhost:8765"
#     async with websockets.connect(uri) as websocket:
#         print("🧪 WebSocket connected!")
#         while True:
#             try:
#                 msg = await websocket.recv()
#                 print(f"📥 Received message: {msg}")
#                 latest_gesture.update(json.loads(msg))
#                 print(f"🧠 Updated gesture_data: {latest_gesture}")
#                 gesture_event.set()
#             except websockets.ConnectionClosed:
#                 print("❌ WebSocket connection closed")
#                 break

# async def main():
#     await listen_for_gestures()

# if __name__ == "__main__":
#     asyncio.run(main())

# import asyncio
# import websockets
# import json

# latest_gesture = {"gesture": None}

# async def handle_connection(uri):
#     async with websockets.connect(uri) as websocket:
#         print("🧪 WebSocket connected!")

#         async def send_loop():
#             while True:
#                 gesture = input("✋ Enter gesture to send (or 'exit'): ")
#                 if gesture == "exit":
#                     break
#                 msg = json.dumps({"gesture": gesture})
#                 await websocket.send(msg)
#                 print(f"📨 Sent: {msg}")

#         async def receive_loop():
#             while True:
#                 msg = await websocket.recv()
#                 print(f"📥 Received: {msg}")
#                 latest_gesture.update(json.loads(msg))

#         await asyncio.gather(send_loop(), receive_loop())

# if __name__ == "__main__":
#     asyncio.run(handle_connection("ws://localhost:8765"))


import asyncio
import websockets
import json

latest_gesture = {"gesture": None}

async def handle_connection(uri):
    async with websockets.connect(uri) as websocket:
        print("🧪 WebSocket connected!")

        # Receive loop: constantly receives gestures from the server
        async def receive_loop():
            while True:
                try:
                    msg = await websocket.recv()
                    print(f"📥 Received: {msg}")
                    latest_gesture.update(json.loads(msg))  # Update the gesture from the server
                except websockets.ConnectionClosed:
                    print("❌ WebSocket connection closed")
                    break

        # Send loop: sends gestures to the server when the model detects one
        async def send_loop():
            while True:
                if latest_gesture["gesture"]:
                    gesture = latest_gesture["gesture"]  # Get the latest gesture
                    msg = json.dumps({"gesture": gesture})
                    await websocket.send(msg)
                    print(f"📨 Sent: {msg}")
                    latest_gesture["gesture"] = None  # Clear gesture after sending

                await asyncio.sleep(0.1)  # Avoid busy-waiting and too frequent sending

        # Run both loops concurrently
        await asyncio.gather(receive_loop(), send_loop())

if __name__ == "__main__":
    uri = "ws://localhost:8765"  # Your WebSocket server address
    asyncio.run(handle_connection(uri))
