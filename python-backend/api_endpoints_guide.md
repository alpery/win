# API Endpoints Guide

This document provides information about the API endpoints available in the Python backend and examples of how to test them.

## Endpoints Overview

The backend provides the following endpoints:

1. **Root Endpoint** (`/`): A simple health check endpoint
2. **Main WebSocket Endpoint** (`/ws`): Handles audio data and text for speech recognition and weather queries

## Detailed Endpoint Information

### 1. Root Endpoint

- **URL**: `/`
- **Method**: GET
- **Description**: Simple health check endpoint that confirms the API is running
- **Response Format**:
  ```json
  {
    "message": "Voice Weather API is running"
  }
  ```

#### Example: Testing with curl

```bash
curl http://localhost:8765/
```

### 2. Main WebSocket Endpoint

- **URL**: `/ws`
- **Protocol**: WebSocket
- **Description**: Handles audio data for speech recognition and text input for weather queries
- **Request Formats**:
  - **Audio Data**:
    ```
    Binary audio data in WAV format sent in the "bytes" field
    ```
  - **Text Data**:
    ```json
    {
      "text": "Wie ist das Wetter in Berlin?"
    }
    ```
- **Response Formats**:
  - **Transcription Response**:
    ```json
    {
      "type": "transcription",
      "text": "Transcribed text and weather information"
    }
    ```
  - **Error Response**:
    ```json
    {
      "type": "error",
      "message": "Error message"
    }
    ```

#### Example: Testing with JavaScript

```javascript
// Example using browser WebSocket API
const socket = new WebSocket('ws://localhost:8765/ws');

socket.onopen = function(e) {
  console.log('Connection established');

  // Example: Sending text data
  socket.send(JSON.stringify({
    text: "Wie ist das Wetter in Berlin?"
  }));
};

socket.onmessage = function(event) {
  console.log('Data received from server:', JSON.parse(event.data));
};

socket.onclose = function(event) {
  if (event.wasClean) {
    console.log(`Connection closed cleanly, code=${event.code} reason=${event.reason}`);
  } else {
    console.log('Connection died');
  }
};

socket.onerror = function(error) {
  console.log(`WebSocket Error: ${error.message}`);
};
```

#### Example: Testing with Python

```python
import asyncio
import websockets
import json

async def test_ws_text():
    uri = "ws://localhost:8765/ws"
    async with websockets.connect(uri) as websocket:
        # Example: Sending text data
        await websocket.send(json.dumps({
            "text": "Wie ist das Wetter in Berlin?"
        }))

        response = await websocket.recv()
        print(f"Received: {response}")

# For audio data, you would need to read a WAV file and send the binary data
async def test_ws_audio():
    uri = "ws://localhost:8765/ws"
    async with websockets.connect(uri) as websocket:
        with open("test_audio.wav", "rb") as audio_file:
            audio_data = audio_file.read()
            await websocket.send(audio_data)

        response = await websocket.recv()
        print(f"Received: {response}")

# Run the test
asyncio.get_event_loop().run_until_complete(test_ws_text())
```


## Running the Server

To run the server, use the following command:

```bash
python main.py
```

This will start the server on `localhost:8765`.
