"""
🎮 SQUAT BIRD GAME - Streamlit Web Version
Online versie van de Squat Bird game!
"""

import streamlit as st
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
import av

# Page config
st.set_page_config(
    page_title="🐦 Squat Bird Game",
    page_icon="🐦",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    font-size: 3rem;
    color: #FF6B6B;
    text-align: center;
    margin-bottom: 2rem;
}
.game-stats {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
}
.instructions {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #28a745;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'total_squats' not in st.session_state:
    st.session_state.total_squats = 0
if 'total_calories' not in st.session_state:
    st.session_state.total_calories = 0.0
if 'game_score' not in st.session_state:
    st.session_state.game_score = 0

class SquatDetector(VideoTransformerBase):
    def __init__(self):
        self.squatting = False
        self.reference_y = 0.5
        
    def detect_squat(self, frame):
        # Simpele beweging detectie (placeholder)
        # In echte versie zou je MediaPipe gebruiken
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detecteer beweging (zeer simpel)
        height, width = gray.shape
        center_region = gray[height//3:2*height//3, width//3:2*width//3]
        brightness = np.mean(center_region)
        
        # Squat detectie op basis van helderheid verandering
        was_squatting = self.squatting
        self.squatting = brightness < 100  # Simpele threshold
        
        if self.squatting and not was_squatting:
            st.session_state.total_squats += 1
            st.session_state.total_calories += 0.32
            return True
        return False

    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")
        
        # Detecteer squat
        squat_detected = self.detect_squat(img)
        
        # Teken interface
        if self.squatting:
            cv2.putText(img, "SQUATTING!", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
        else:
            cv2.putText(img, "STAND UP!", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
        
        # Reference line
        height, width = img.shape[:2]
        ref_y = int(height * self.reference_y)
        cv2.line(img, (0, ref_y), (width, ref_y), (255, 255, 0), 3)
        
        # Stats overlay
        cv2.putText(img, f"Squats: {st.session_state.total_squats}", 
                   (width-200, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(img, f"Calories: {st.session_state.total_calories:.1f}", 
                   (width-200, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        return av.VideoFrame.from_ndarray(img, format="bgr24")

def main():
    # Header
    st.markdown('<h1 class="main-header">🐦 Squat Bird Game</h1>', unsafe_allow_html=True)
    
    # Layout
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Game area
        st.markdown("### 📹 Squat om punten te verdienen!")
        
        # WebRTC component
        webrtc_ctx = webrtc_streamer(
            key="squat-detector",
            video_processor_factory=SquatDetector,
            media_stream_constraints={"video": True, "audio": False},
            async_processing=True,
        )
        
        # Instructions
        with st.container():
            st.markdown("""
            <div class="instructions">
            <h4>🎮 Hoe te spelen:</h4>
            <ul>
            <li>📸 <strong>Camera toestaan</strong> - Klik "Start" hierboven</li>
            <li>🏋️‍♀️ <strong>Maak squats</strong> - Ga omlaag onder de gele lijn</li>
            <li>📊 <strong>Verdien punten</strong> - Elke squat telt!</li>
            <li>🔥 <strong>Verbrand calorieën</strong> - ~0.32 per squat</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
    
    # Sidebar stats
    with st.sidebar:
        st.markdown("## 📊 Jouw Stats")
        
        # Current session
        st.markdown(f"""
        <div class="game-stats">
        <h3>💪 Totaal Squats</h3>
        <h1>{st.session_state.total_squats}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="game-stats">
        <h3>🔥 Calorieën Verbrand</h3>
        <h1>{st.session_state.total_calories:.1f}</h1>
        </div>
        """, unsafe_allow_html=True)
        
        # Reset button
        if st.button("🔄 Reset Stats", type="secondary"):
            st.session_state.total_squats = 0
            st.session_state.total_calories = 0.0
            st.rerun()
        
        # Info
        st.markdown("---")
        st.markdown("### ℹ️ Info")
        st.markdown("""
        - **Berekening:** 0.32 cal/squat
        - **Gebaseerd op:** 70kg persoon
        - **Type:** Lichte squats
        """)
        
        st.markdown("### 🎯 Tips")
        st.markdown("""
        - Zorg voor goede verlichting
        - Blijf in beeld
        - Maak volledige bewegingen
        - Ga onder de gele lijn
        """)

if __name__ == "__main__":
    main()