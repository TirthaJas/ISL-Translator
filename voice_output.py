import tempfile
import os
import sounddevice as sd
import soundfile as sf
from gtts import gTTS

class VoiceOutput:
    def __init__(self):
        self.device_id = 3

    def speak(self, text, emotion="neutral"):
        if not text or text.strip() == "":
            return False
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tmp_path = tempfile.mktemp(suffix=".mp3")
            tts.save(tmp_path)

            data, samplerate = sf.read(tmp_path)
            sd.play(data, samplerate, device=self.device_id)
            sd.wait()
            os.unlink(tmp_path)
            return True

        except Exception as e:
            print(f"Voice error: {e}")
            return False

    def stop(self):
        sd.stop()