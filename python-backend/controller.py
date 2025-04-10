import os
import tempfile
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from vosk_service import VoskService
from extractorService import WeatherExtractor

# Create FastAPI application
app = FastAPI(
    title="Win Python Backend",
    description="Speech-to-text service for weather queries",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
vosk_service = VoskService()
weather_extractor = WeatherExtractor()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message, websocket):
        await websocket.send_json(message)

manager = ConnectionManager()

# WebSocket endpoint for speech processing
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive()

            # Handle audio data
            if "bytes" in data:
                if not vosk_service.is_available():
                    await manager.send_message(
                        {"type": "error", "message": "Speech recognition not available"},
                        websocket
                    )
                    continue

                audio_data = data["bytes"]
                temp_file_path = None

                try:
                    # Save audio data to temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                        temp_file_path = temp_file.name
                        temp_file.write(audio_data)

                    # Transcribe audio
                    transcription_result = vosk_service.transcribe_audio(temp_file_path)

                    if not transcription_result["success"]:
                        await manager.send_message(
                            {"type": "error", "message": transcription_result["error"]},
                            websocket
                        )
                        continue

                    transcribed_text = transcription_result["text"]

                    # Send transcription to client
                    await manager.send_message(
                        {"type": "transcription", "text": transcribed_text},
                        websocket
                    )

                    if not transcribed_text:
                        await manager.send_message(
                            {"type": "transcription", "text": "Keine Sprache erkannt."},
                            websocket
                        )
                        continue

                    # Extract weather query information
                    weather_data = weather_extractor.extract(transcribed_text)
                    weather_data["original_query"] = transcribed_text

                    # Format response with extracted weather information
                    result_text = f"{transcribed_text}\n\nWetterabfrage: {weather_data.get('is_weather_query')}\nOrt: {weather_data.get('location', 'nicht erkannt')}\nZeitraum: {weather_data.get('time_period', 'heute')}"

                    # Send result to client
                    await manager.send_message(
                        {"type": "transcription", "text": result_text},
                        websocket
                    )

                except Exception as e:
                    await manager.send_message(
                        {"type": "error", "message": f"Error: {str(e)}"},
                        websocket
                    )
                finally:
                    # Clean up temporary file
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)

            # Handle text input (for testing without audio)
            elif "text" in data:
                try:
                    text_query = data["text"]

                    # Extract weather query information
                    weather_data = weather_extractor.extract(text_query)
                    weather_data["original_query"] = text_query

                    # Format response with extracted weather information
                    result_text = f"{text_query}\n\nWetterabfrage: {weather_data.get('is_weather_query')}\nOrt: {weather_data.get('location', 'nicht erkannt')}\nZeitraum: {weather_data.get('time_period', 'heute')}"

                    # Send result to client
                    await manager.send_message(
                        {"type": "transcription", "text": result_text},
                        websocket
                    )

                except Exception as e:
                    await manager.send_message(
                        {"type": "error", "message": f"Error: {str(e)}"},
                        websocket
                    )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": "Voice Weather API is running",
        "status": "healthy",
        "services": {
            "vosk": vosk_service.is_available(),
            "weather_extractor": True
        }
    }
