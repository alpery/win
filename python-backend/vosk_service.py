import json
import os
import wave
from typing import Dict, Any

# Try to import Vosk, but don't fail if it's not available
try:
    from vosk import Model, KaldiRecognizer
    vosk_available = True
except ImportError:
    vosk_available = False
    print("Warning: Vosk not available. Speech recognition will not work.")


class VoskService:
    """
    Service for speech-to-text conversion using the Vosk library.
    """

    def __init__(self, model_path: str = "model/vosk-model-small-de-0.15"):
        """
        Initialize the VoskService.

        Args:
            model_path: Path to the Vosk model directory
        """
        self.model = None
        self.model_path = model_path
        self.initialize_model()

    def initialize_model(self) -> bool:
        """
        Initialize the Vosk model.

        Returns:
            True if the model was successfully initialized, False otherwise
        """
        if not vosk_available:
            return False

        if os.path.exists(self.model_path):
            try:
                self.model = Model(self.model_path)
                return True
            except Exception as e:
                print(f"Error initializing Vosk model: {e}")
                return False
        else:
            print(f"Model path not found: {self.model_path}")
            return False

    def is_available(self) -> bool:
        """
        Check if speech recognition is available.

        Returns:
            True if Vosk is available and the model is initialized, False otherwise
        """
        return vosk_available and self.model is not None

    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file to text.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            Dictionary with:
                - success: Whether the transcription was successful
                - text: The transcribed text (if successful)
                - error: Error message (if not successful)
        """
        if not self.is_available():
            return {"success": False, "error": "Speech recognition not available"}

        try:
            # Open audio file
            wf = wave.open(audio_file_path, "rb")

            # Initialize recognizer
            rec = KaldiRecognizer(self.model, wf.getframerate())

            # Process audio in chunks
            result = ""
            while True:
                data_chunk = wf.readframes(4000)
                if len(data_chunk) == 0:
                    break

                if rec.AcceptWaveform(data_chunk):
                    part_result = json.loads(rec.Result())
                    result += part_result.get("text", "") + " "

            # Get final result
            final_result = json.loads(rec.FinalResult())
            result += final_result.get("text", "")

            return {
                "success": True,
                "text": result.strip()
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
