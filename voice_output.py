import tempfile
import os
from gtts import gTTS
import streamlit as st

class VoiceOutput:
    def __init__(self):
        pass

    def speak(self, text, emotion="neutral"):
        if not text or text.strip() == "":
            return False
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tmp_path = tempfile.mktemp(suffix=".mp3")
            tts.save(tmp_path)
            with open(tmp_path, "rb") as f:
                audio_bytes = f.read()
            st.audio(audio_bytes, format="audio/mp3", autoplay=True)
            os.unlink(tmp_path)
            return True
        except Exception as e:
            print(f"Voice error: {e}")
            return False

    def stop(self):
        pass