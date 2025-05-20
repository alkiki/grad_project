const socket = new WebSocket("ws://localhost:8765");

socket.onopen = () => {
    console.log("WebSocket connected!");
};

socket.onmessage = (event) => {
    try {
        // Parse the incoming message as JSON
        const message = JSON.parse(event.data);
        console.log("Received gesture:", message.gesture);
    } catch (error) {
        console.error("Error parsing message:", error);
    }
};

socket.onerror = (error) => {
    console.error("WebSocket error:", error);
};

// Example: sending a gesture as a JSON object
function sendGesture(gesture) {
    const message = JSON.stringify({ gesture: gesture });
    socket.send(message);
    console.log("📨 Gesture sent:", message);
}

// Send a test gesture (you can replace this with actual gesture data)
sendGesture('swipe_left');

