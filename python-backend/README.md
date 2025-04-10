# Win Python Backend

This is a Python backend service for the Win application. It provides speech-to-text functionality using the Vosk library and extracts weather-related information from text.

## Overview

The Python backend serves as a bridge between clients and the application. It:

1. Receives audio data from clients via WebSocket
2. Transcribes the audio to text using Vosk
3. Extracts weather-related information from the text
4. Returns the results to the client

## Components

- **main.py**: Entry point for the FastAPI application
- **controller.py**: Defines the API endpoints and WebSocket handler
- **vosk_service.py**: Handles speech-to-text conversion using Vosk
- **extractorService.py**: Extracts weather-related information from text

## API Endpoints

- `GET /`: Health check endpoint
- `WebSocket /ws`: WebSocket endpoint for speech processing

## Usage

1. Start the server:
   ```
   python main.py
   ```

2. Connect to the WebSocket endpoint at `ws://localhost:8765/ws`

3. Send audio data as binary or text data as JSON:
   ```json
   {"text": "Wetter Berlin"}
   ```

4. Receive transcription and weather data as JSON:
   ```json
   {"type": "transcription", "text": "Wetter Berlin\n\nWetterabfrage: true\nOrt: berlin\nZeitraum: heute"}
   ```

## Dependencies

- FastAPI
- Uvicorn
- Vosk (for speech recognition)
