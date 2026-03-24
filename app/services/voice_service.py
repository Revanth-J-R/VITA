import os
import uuid
import base64
from gtts import gTTS

class VoiceService:
    def __init__(self):
        self.output_dir = os.path.join("app", "static", "audio")
        os.makedirs(self.output_dir, exist_ok=True)

    def transcribe_audio(self, file_path: str) -> str:
        # This was the Whisper-based transcription, now handled by the client's Web Speech API.
        return ""


    def generate_speech(self, text: str) -> str:
        """
        Convert text to speech using gTTS and return base64 string.
        """
        if not text:
            return ""
            
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            filename = f"{uuid.uuid4()}.mp3"
            filepath = os.path.join(self.output_dir, filename)
            tts.save(filepath)
            
            with open(filepath, "rb") as audio_file:
                encoded_string = base64.b64encode(audio_file.read()).decode('utf-8')
            
            try:
                os.remove(filepath)
            except:
                pass
                
            return encoded_string
        except Exception as e:
            print(f"Speech generation error: {e}")
            return ""

    def get_status(self) -> dict:
        return {
            "loaded": True,
            "mode": "Web Speech API (Browser Native)"
        }

voice_service = VoiceService()
