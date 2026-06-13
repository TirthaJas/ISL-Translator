import cv2
import streamlit as st
import numpy as np
from hand_tracker import HandTracker
from face_tracker import FaceTracker
from isl_recognizer import ISLRecognizer
from llm_translator import LLMTranslator
from voice_output import VoiceOutput
import threading
import time

st.set_page_config(
    page_title="ISL Translator",
    page_icon="🤟",
    layout="wide"
)

st.markdown("""
<style>
/* Hide streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Dark background */
.main, .block-container {
    background-color: #0a0a0a !important;
    padding: 0 !important;
    max-width: 100% !important;
}

/* Title */
.app-title {
    text-align: center;
    font-size: 2.5em;
    font-weight: 800;
    color: #ffffff;
    padding: 15px 0 5px 0;
    letter-spacing: 2px;
}

.app-subtitle {
    text-align: center;
    font-size: 1em;
    color: #888888;
    margin-bottom: 20px;
    letter-spacing: 1px;
}

/* Emotion pills */
.emotion-pill {
    display: inline-block;
    padding: 8px 18px;
    border-radius: 20px;
    margin: 4px;
    font-size: 0.9em;
    font-weight: 600;
    cursor: default;
}

.emotion-active {
    background-color: #00ff88;
    color: #000000;
}

.emotion-inactive {
    background-color: #1a1a1a;
    color: #666666;
    border: 1px solid #333;
}

/* Current sign display */
.sign-display {
    background: rgba(0,0,0,0.7);
    border: 2px solid #00ff88;
    border-radius: 15px;
    padding: 20px;
    text-align: center;
    margin: 10px 0;
}

.sign-word {
    font-size: 3em;
    font-weight: 900;
    color: #ffffff;
    letter-spacing: 3px;
}

.sign-subtitle {
    font-size: 0.8em;
    color: #00ff88;
    letter-spacing: 2px;
}

/* Signs collected */
.signs-collected {
    background: #111111;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    border: 1px solid #222;
    min-height: 60px;
    color: #ffffff;
    font-size: 1.1em;
    letter-spacing: 1px;
}

/* Translation box */
.translation-box {
    background: #0d1f0d;
    border: 1px solid #00ff88;
    border-radius: 12px;
    padding: 15px;
    margin: 10px 0;
    color: #00ff88;
    font-size: 1.1em;
    min-height: 60px;
}

/* Buttons */
.stButton > button {
    background-color: #00ff88 !important;
    color: #000000 !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    border: none !important;
    padding: 10px !important;
    font-size: 1em !important;
    width: 100% !important;
}

.stButton > button:hover {
    background-color: #00cc6a !important;
}

/* Section labels */
.section-label {
    color: #888888;
    font-size: 0.8em;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 5px;
}

/* Divider */
hr {
    border-color: #222222 !important;
}
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="app-title">🤟 ISL TRANSLATOR</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">Indian Sign Language → English Voice</div>', unsafe_allow_html=True)

# Initialize session state
if "recognizer" not in st.session_state:
    st.session_state.recognizer = ISLRecognizer()
if "translator" not in st.session_state:
    st.session_state.translator = LLMTranslator()
if "voice" not in st.session_state:
    st.session_state.voice = VoiceOutput()
if "hand_tracker" not in st.session_state:
    st.session_state.hand_tracker = HandTracker()
if "face_tracker" not in st.session_state:
    st.session_state.face_tracker = FaceTracker()
if "current_sentence" not in st.session_state:
    st.session_state.current_sentence = []
if "emotion" not in st.session_state:
    st.session_state.emotion = "neutral"
if "translation" not in st.session_state:
    st.session_state.translation = ""
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "current_sign" not in st.session_state:
    st.session_state.current_sign = None

# Layout
col1, col2 = st.columns([3, 2])

with col1:
    # Camera feed
    camera_placeholder = st.empty()

    # Control buttons
    b1, b2, b3 = st.columns(3)
    with b1:
        start_btn = st.button("▶  Start", use_container_width=True)
    with b2:
        stop_btn = st.button("⏹  Stop", use_container_width=True)
    with b3:
        clear_btn = st.button("🗑  Clear", use_container_width=True)

with col2:
    # Emotion pills
    st.markdown('<div class="section-label">Emotion Detected</div>', unsafe_allow_html=True)
    emotion_placeholder = st.empty()

    st.markdown("---")

    # Current sign
    st.markdown('<div class="section-label">Current Sign</div>', unsafe_allow_html=True)
    sign_placeholder = st.empty()

    # Signs collected
    st.markdown('<div class="section-label">Signs Collected</div>', unsafe_allow_html=True)
    sentence_placeholder = st.empty()

    st.markdown("---")

    # Translation
    st.markdown('<div class="section-label">Translation</div>', unsafe_allow_html=True)
    translation_placeholder = st.empty()

    # Action buttons
    translate_btn = st.button("🧠  Translate Now", use_container_width=True)
    speak_btn = st.button("🔊  Speak Translation", use_container_width=True)

# Emotion definitions
emotions = ["happy", "sad", "neutral", "angry", "surprised", "disgusted"]
emotion_emojis = {
    "happy": "😄 Happy",
    "sad": "😢 Sad",
    "neutral": "😐 Neutral",
    "angry": "😠 Angry",
    "surprised": "😲 Surprised",
    "disgusted": "🤢 Disgusted"
}

def render_emotions(current_emotion):
    html = '<div style="display:flex; flex-wrap:wrap; gap:5px;">'
    for e in emotions:
        if e == current_emotion:
            html += f'<span class="emotion-pill emotion-active">{emotion_emojis[e]}</span>'
        else:
            html += f'<span class="emotion-pill emotion-inactive">{emotion_emojis[e]}</span>'
    html += '</div>'
    return html

# Handle buttons
if clear_btn:
    st.session_state.recognizer.clear_sentence()
    st.session_state.translation = ""
    st.session_state.current_sign = None

if start_btn:
    st.session_state.is_running = True

if stop_btn:
    st.session_state.is_running = False

if translate_btn:
    sentence = st.session_state.recognizer.get_sentence()
    if sentence:
        with st.spinner("Translating with Ollama..."):
            _, result = st.session_state.translator.translate(
                sentence,
                st.session_state.emotion
            )
            st.session_state.translation = result
    else:
        st.warning("No signs collected yet!")

if speak_btn:
    if st.session_state.translation:
        with st.spinner("Speaking..."):
            threading.Thread(
                target=st.session_state.voice.speak,
                args=(st.session_state.translation, st.session_state.emotion),
                daemon=True
            ).start()
    else:
        st.warning("Nothing to speak! Translate first.")

# Update static placeholders
emotion_placeholder.markdown(
    render_emotions(st.session_state.emotion),
    unsafe_allow_html=True
)

sign_placeholder.markdown(
    f'''<div class="sign-display">
        <div class="sign-word">{st.session_state.current_sign if st.session_state.current_sign else "---"}</div>
        <div class="sign-subtitle">DETECTED SIGN</div>
    </div>''',
    unsafe_allow_html=True
)

sentence_placeholder.markdown(
    f'<div class="signs-collected">{" → ".join(st.session_state.current_sentence) if st.session_state.current_sentence else "No signs yet..."}</div>',
    unsafe_allow_html=True
)

translation_placeholder.markdown(
    f'<div class="translation-box">{st.session_state.translation if st.session_state.translation else "Press Translate Now..."}</div>',
    unsafe_allow_html=True
)

# Camera loop
if st.session_state.is_running:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while st.session_state.is_running:
        ret, frame = cap.read()
        if not ret:
            st.error("Camera not found!")
            break

        frame = cv2.flip(frame, 1)

        # Hand tracking
        frame, hand_landmarks = st.session_state.hand_tracker.find_hands(frame)

        # Face tracking
        frame, face_landmarks = st.session_state.face_tracker.find_face(frame)

        # Detect emotion
        emotion = st.session_state.face_tracker.detect_emotion(face_landmarks)
        st.session_state.emotion = emotion

        # Recognize sign
        current_sign = None
        if hand_landmarks:
            finger_states = st.session_state.hand_tracker.get_finger_states(
                hand_landmarks[0]
            )
            current_sign = st.session_state.recognizer.recognize_sign(finger_states)
            if current_sign:
                st.session_state.current_sentence = st.session_state.recognizer.update_sentence(current_sign)

        st.session_state.current_sign = current_sign

        # Update UI
        emotion_placeholder.markdown(
            render_emotions(emotion),
            unsafe_allow_html=True
        )

        sign_placeholder.markdown(
            f'''<div class="sign-display">
                <div class="sign-word">{current_sign if current_sign else "---"}</div>
                <div class="sign-subtitle">DETECTED SIGN</div>
            </div>''',
            unsafe_allow_html=True
        )

        sentence_placeholder.markdown(
            f'<div class="signs-collected">{" → ".join(st.session_state.current_sentence) if st.session_state.current_sentence else "No signs yet..."}</div>',
            unsafe_allow_html=True
        )

        translation_placeholder.markdown(
            f'<div class="translation-box">{st.session_state.translation if st.session_state.translation else "Press Translate Now..."}</div>',
            unsafe_allow_html=True
        )

        # Show frame
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        camera_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

        time.sleep(0.03)

    cap.release()

else:
    camera_placeholder.markdown(
        '''<div style="background:#111111; border-radius:15px; height:400px; 
        display:flex; align-items:center; justify-content:center; 
        color:#444444; font-size:1.5em; border: 1px solid #222;">
        Press ▶ Start to begin</div>''',
        unsafe_allow_html=True
    )