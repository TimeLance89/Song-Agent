"""
Enhanced UI Components für den KI Song-Agent
Verbesserte visuelle Elemente für den Anzeigeprozess
"""

import streamlit as st
import time
from typing import Dict, List

def get_genre_colors(genre: str) -> Dict[str, str]:
    """Gibt genre-spezifische Farbschemata zurück"""
    color_schemes = {
        "Deep House": {
            "primary": "#1a1a2e",
            "secondary": "#16213e", 
            "accent": "#0f3460",
            "highlight": "#533483"
        },
        "Synthpop": {
            "primary": "#ff006e",
            "secondary": "#8338ec",
            "accent": "#3a86ff",
            "highlight": "#06ffa5"
        },
        "Trap": {
            "primary": "#2d2d2d",
            "secondary": "#ff6b35",
            "accent": "#f7931e",
            "highlight": "#ffb627"
        },
        "Techno": {
            "primary": "#000000",
            "secondary": "#333333",
            "accent": "#666666",
            "highlight": "#00ff00"
        },
        "Ambient": {
            "primary": "#e8f4f8",
            "secondary": "#b8d4da",
            "accent": "#88b4bc",
            "highlight": "#5894a0"
        },
        "Drum & Bass": {
            "primary": "#1a0033",
            "secondary": "#330066",
            "accent": "#4d0099",
            "highlight": "#6600cc"
        },
        "Future Bass": {
            "primary": "#ff0080",
            "secondary": "#8000ff",
            "accent": "#0080ff",
            "highlight": "#00ffff"
        },
        "Lo-Fi Hip Hop": {
            "primary": "#8b4513",
            "secondary": "#cd853f",
            "accent": "#daa520",
            "highlight": "#ffd700"
        },
        "Psytrance": {
            "primary": "#4b0082",
            "secondary": "#8a2be2",
            "accent": "#9932cc",
            "highlight": "#da70d6"
        },
        "Indie Pop": {
            "primary": "#ff69b4",
            "secondary": "#ff1493",
            "accent": "#dc143c",
            "highlight": "#b22222"
        },
        "Hardstyle": {
            "primary": "#ff0000",
            "secondary": "#cc0000",
            "accent": "#990000",
            "highlight": "#ffff00"
        }
    }
    return color_schemes.get(genre, color_schemes["Deep House"])

def create_animated_progress_bar(progress: float, phase: str, genre: str = "Deep House") -> str:
    """Erstellt einen animierten Fortschrittsbalken mit genre-spezifischen Farben"""
    colors = get_genre_colors(genre)
    
    return f"""
    <div style="margin: 20px 0;">
        <div style="
            background: linear-gradient(90deg, {colors['primary']}, {colors['secondary']});
            border-radius: 25px;
            padding: 3px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        ">
            <div style="
                background: linear-gradient(90deg, {colors['accent']}, {colors['highlight']});
                width: {progress}%;
                height: 30px;
                border-radius: 22px;
                transition: width 0.5s ease-in-out;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: 14px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
                animation: pulse 2s infinite;
            ">
                {progress:.0f}%
            </div>
        </div>
        <div style="
            text-align: center;
            margin-top: 10px;
            font-size: 16px;
            font-weight: bold;
            color: {colors['accent']};
            animation: fadeInOut 2s infinite;
        ">
            {phase}
        </div>
    </div>
    
    <style>
        @keyframes pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.02); }}
            100% {{ transform: scale(1); }}
        }}
        
        @keyframes fadeInOut {{
            0% {{ opacity: 0.7; }}
            50% {{ opacity: 1; }}
            100% {{ opacity: 0.7; }}
        }}
    </style>
    """

def create_floating_music_notes(genre: str = "Deep House") -> str:
    """Erstellt schwebende Musiknoten-Animation"""
    colors = get_genre_colors(genre)
    
    return f"""
    <div class="music-notes-container">
        <div class="music-note note1">♪</div>
        <div class="music-note note2">♫</div>
        <div class="music-note note3">♪</div>
        <div class="music-note note4">♬</div>
        <div class="music-note note5">♫</div>
    </div>
    
    <style>
        .music-notes-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1000;
        }}
        
        .music-note {{
            position: absolute;
            font-size: 24px;
            color: {colors['highlight']};
            opacity: 0.7;
            animation: floatUp 8s infinite linear;
        }}
        
        .note1 {{
            left: 10%;
            animation-delay: 0s;
        }}
        
        .note2 {{
            left: 25%;
            animation-delay: 2s;
        }}
        
        .note3 {{
            left: 50%;
            animation-delay: 4s;
        }}
        
        .note4 {{
            left: 75%;
            animation-delay: 6s;
        }}
        
        .note5 {{
            left: 90%;
            animation-delay: 1s;
        }}
        
        @keyframes floatUp {{
            0% {{
                transform: translateY(100vh) rotate(0deg);
                opacity: 0;
            }}
            10% {{
                opacity: 0.7;
            }}
            90% {{
                opacity: 0.7;
            }}
            100% {{
                transform: translateY(-100px) rotate(360deg);
                opacity: 0;
            }}
        }}
    </style>
    """

def create_ai_avatar_animation(genre: str = "Deep House") -> str:
    """Erstellt einen pulsierenden KI-Avatar"""
    colors = get_genre_colors(genre)
    
    return f"""
    <div style="
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 30px 0;
    ">
        <div class="ai-avatar">
            🤖
        </div>
    </div>
    
    <style>
        .ai-avatar {{
            font-size: 80px;
            animation: aiPulse 2s infinite;
            filter: drop-shadow(0 0 20px {colors['highlight']});
        }}
        
        @keyframes aiPulse {{
            0% {{
                transform: scale(1);
                filter: drop-shadow(0 0 20px {colors['highlight']});
            }}
            50% {{
                transform: scale(1.1);
                filter: drop-shadow(0 0 30px {colors['accent']});
            }}
            100% {{
                transform: scale(1);
                filter: drop-shadow(0 0 20px {colors['highlight']});
            }}
        }}
    </style>
    """

def create_waveform_animation(genre: str = "Deep House") -> str:
    """Erstellt eine Wellenform-Animation"""
    colors = get_genre_colors(genre)
    
    return f"""
    <div class="waveform-container">
        <div class="wave-bar bar1"></div>
        <div class="wave-bar bar2"></div>
        <div class="wave-bar bar3"></div>
        <div class="wave-bar bar4"></div>
        <div class="wave-bar bar5"></div>
        <div class="wave-bar bar6"></div>
        <div class="wave-bar bar7"></div>
        <div class="wave-bar bar8"></div>
    </div>
    
    <style>
        .waveform-container {{
            display: flex;
            justify-content: center;
            align-items: end;
            height: 60px;
            margin: 20px 0;
            gap: 3px;
        }}
        
        .wave-bar {{
            width: 8px;
            background: linear-gradient(to top, {colors['accent']}, {colors['highlight']});
            border-radius: 4px;
            animation: waveform 1.5s infinite ease-in-out;
        }}
        
        .bar1 {{ animation-delay: 0s; }}
        .bar2 {{ animation-delay: 0.1s; }}
        .bar3 {{ animation-delay: 0.2s; }}
        .bar4 {{ animation-delay: 0.3s; }}
        .bar5 {{ animation-delay: 0.4s; }}
        .bar6 {{ animation-delay: 0.5s; }}
        .bar7 {{ animation-delay: 0.6s; }}
        .bar8 {{ animation-delay: 0.7s; }}
        
        @keyframes waveform {{
            0%, 100% {{
                height: 10px;
            }}
            50% {{
                height: 50px;
            }}
        }}
    </style>
    """

def create_status_card(title: str, message: str, genre: str = "Deep House", show_time: bool = True) -> str:
    """Erstellt eine animierte Status-Karte"""
    colors = get_genre_colors(genre)
    current_time = time.strftime("%H:%M:%S") if show_time else ""
    
    return f"""
    <div class="status-card">
        <div class="status-header">
            <h3>{title}</h3>
            {f'<span class="timestamp">{current_time}</span>' if show_time else ''}
        </div>
        <div class="status-message">
            {message}
        </div>
    </div>
    
    <style>
        .status-card {{
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            border-radius: 15px;
            padding: 20px;
            margin: 15px 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            border: 2px solid {colors['accent']};
            animation: slideInFromLeft 0.5s ease-out;
        }}
        
        .status-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        
        .status-header h3 {{
            color: {colors['highlight']};
            margin: 0;
            font-size: 18px;
        }}
        
        .timestamp {{
            color: {colors['accent']};
            font-size: 12px;
            opacity: 0.8;
        }}
        
        .status-message {{
            color: white;
            font-size: 14px;
            line-height: 1.4;
        }}
        
        @keyframes slideInFromLeft {{
            0% {{
                transform: translateX(-100%);
                opacity: 0;
            }}
            100% {{
                transform: translateX(0);
                opacity: 1;
            }}
        }}
    </style>
    """

def create_enhanced_loading_spinner(genre: str = "Deep House") -> str:
    """Erstellt einen verbesserten Loading-Spinner"""
    colors = get_genre_colors(genre)
    
    return f"""
    <div class="enhanced-spinner-container">
        <div class="enhanced-spinner">
            <div class="spinner-ring ring1"></div>
            <div class="spinner-ring ring2"></div>
            <div class="spinner-ring ring3"></div>
            <div class="spinner-center">🎵</div>
        </div>
    </div>
    
    <style>
        .enhanced-spinner-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 30px 0;
        }}
        
        .enhanced-spinner {{
            position: relative;
            width: 100px;
            height: 100px;
        }}
        
        .spinner-ring {{
            position: absolute;
            border-radius: 50%;
            border: 3px solid transparent;
        }}
        
        .ring1 {{
            width: 100px;
            height: 100px;
            border-top: 3px solid {colors['highlight']};
            animation: spin 2s linear infinite;
        }}
        
        .ring2 {{
            width: 80px;
            height: 80px;
            top: 10px;
            left: 10px;
            border-right: 3px solid {colors['accent']};
            animation: spin 1.5s linear infinite reverse;
        }}
        
        .ring3 {{
            width: 60px;
            height: 60px;
            top: 20px;
            left: 20px;
            border-bottom: 3px solid {colors['secondary']};
            animation: spin 1s linear infinite;
        }}
        
        .spinner-center {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: 24px;
            animation: pulse 2s infinite;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
    """

def show_enhanced_progress(phase: str, progress: float, genre: str, additional_info: str = "") -> None:
    """Zeigt den verbesserten Fortschritt mit allen visuellen Elementen an"""
    
    # Container für alle visuellen Elemente
    progress_container = st.container()
    
    with progress_container:
        # Schwebende Musiknoten im Hintergrund
        st.markdown(create_floating_music_notes(genre), unsafe_allow_html=True)
        
        # KI-Avatar Animation
        st.markdown(create_ai_avatar_animation(genre), unsafe_allow_html=True)
        
        # Hauptfortschrittsbalken
        st.markdown(create_animated_progress_bar(progress, phase, genre), unsafe_allow_html=True)
        
        # Wellenform-Animation
        st.markdown(create_waveform_animation(genre), unsafe_allow_html=True)
        
        # Status-Karte mit zusätzlichen Informationen
        if additional_info:
            st.markdown(create_status_card("Status Update", additional_info, genre), unsafe_allow_html=True)
        
        # Loading-Spinner für aktive Phasen
        if progress < 100:
            st.markdown(create_enhanced_loading_spinner(genre), unsafe_allow_html=True)

def create_completion_celebration(genre: str) -> str:
    """Erstellt eine Feier-Animation für die Fertigstellung"""
    colors = get_genre_colors(genre)
    
    return f"""
    <div class="celebration-container">
        <div class="celebration-text">🎉 Song erfolgreich erstellt! 🎉</div>
        <div class="confetti">
            <div class="confetti-piece piece1">🎵</div>
            <div class="confetti-piece piece2">🎶</div>
            <div class="confetti-piece piece3">🎼</div>
            <div class="confetti-piece piece4">🎵</div>
            <div class="confetti-piece piece5">🎶</div>
        </div>
    </div>
    
    <style>
        .celebration-container {{
            text-align: center;
            margin: 30px 0;
            position: relative;
        }}
        
        .celebration-text {{
            font-size: 24px;
            font-weight: bold;
            color: {colors['highlight']};
            animation: celebrationBounce 1s ease-in-out infinite;
        }}
        
        .confetti {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100px;
        }}
        
        .confetti-piece {{
            position: absolute;
            font-size: 20px;
            animation: confettiFall 3s ease-out infinite;
        }}
        
        .piece1 {{ left: 10%; animation-delay: 0s; }}
        .piece2 {{ left: 30%; animation-delay: 0.5s; }}
        .piece3 {{ left: 50%; animation-delay: 1s; }}
        .piece4 {{ left: 70%; animation-delay: 1.5s; }}
        .piece5 {{ left: 90%; animation-delay: 2s; }}
        
        @keyframes celebrationBounce {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.1); }}
        }}
        
        @keyframes confettiFall {{
            0% {{
                transform: translateY(-100px) rotate(0deg);
                opacity: 1;
            }}
            100% {{
                transform: translateY(200px) rotate(360deg);
                opacity: 0;
            }}
        }}
    </style>
    """

