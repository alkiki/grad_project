# Created with assistance from ChatGPT (OpenAI)
import asyncio
import websockets
import json

connected_clients = set()
latest_gesture = None

async def handler(websocket):  
    global latest_gesture
    connected_clients.add(websocket)
    try:
        # Receive messages from the client
        async for message in websocket:
            print(f"📥 Received raw message: {message}")
            try:
                message_data = json.loads(message)  # Expecting {"gesture": "swipe_left"}
                print(f"📨 Gesture received: {message_data['gesture']}")
                latest_gesture = message_data["gesture"]
                response = json.dumps({"gesture": latest_gesture})  # Send the message as JSON
                for client in connected_clients:
                    await client.send(response)
            except json.JSONDecodeError as e:
                print(f"❌ Error parsing message: {message} -> {e}")
    except websockets.ConnectionClosed:
        print("❌ Client disconnected")
    finally:
        connected_clients.remove(websocket)


# Main function to start the server.
async def main():
    print("🌐 WebSocket server started on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Keep the server running indefinitely

if __name__ == "__main__":
    asyncio.run(main())  # Run the WebSocket server
