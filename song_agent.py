"""
KI Song-Agent – Automatische Songtext-Generierung mit Ollama + Suno API
------------------------------------------------------------------------
• Generiert automatisch Songtexte basierend auf Beschreibungen
• Verwendet Ollama für Lyrics-Erstellung
• Erstellt komplette Songs mit Suno API
• Automatische Stilbeschreibung basierend auf Genre-Auswahl
• Live-Anzeige der Stilbedeutung
• Verbesserte visuelle Anzeige während der KI-Arbeit
"""

import time
import textwrap
import json
import re
import toml
import os
from datetime import datetime

import requests
import streamlit as st
from enhanced_ui_components import (
    show_enhanced_progress, 
    create_completion_celebration,
    get_genre_colors
)

# -------------------------------------------------------------------------
# 0) Configuration Management
# -------------------------------------------------------------------------
CONFIG_FILE = "config.toml"

def load_config():
    """Load configuration from config.toml"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return toml.load(f)
        else:
            # Create default config if it doesn't exist
            default_config = {"general": {"language": "de"}}
            save_config(default_config)
            return default_config
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return {"general": {"language": "de"}}

def save_config(config):
    """Save configuration to config.toml"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            toml.dump(config, f)
    except Exception as e:
        st.error(f"Error saving config: {e}")

def get_saved_language():
    """Get saved language from config"""
    config = load_config()
    return config.get("general", {}).get("language", "de")

def save_language(language):
    """Save language to config"""
    config = load_config()
    if "general" not in config:
        config["general"] = {}
    config["general"]["language"] = language
    save_config(config)

# -------------------------------------------------------------------------
# 1) Language Support System
# -------------------------------------------------------------------------
LANGUAGES = {
    "en": "English",
    "de": "Deutsch"
}

TRANSLATIONS = {
    "en": {
        "app_title": "🤖 AI Song Agent",
        "app_subtitle": "Your personal AI assistant for song production",
        "how_it_works": "🎵 How does the Song Agent work?",
        "how_it_works_desc": "Choose a genre and describe your song - the agent automatically creates:",
        "features": [
            "📝 Professional lyrics in the correct format",
            "🎼 Matching style and mood description based on genre",
            "🎧 Complete MP3 file for download",
            "✨ Live style preview when changing genres"
        ],
        "new_feature": "Interactive genre selection with live style preview!",
        "genre_selection": "🎼 Genre Selection",
        "choose_genre": "Choose a genre for automatic style generation:",
        "live_style_preview": "🎯 Live Style Preview",
        "song_config": "🎯 Song Configuration",
        "selected_genre": "🎵 Selected Genre:",
        "instrumental_only": "Instrumental only",
        "custom_style_desc": "🎨 Custom Style Description:",
        "custom_style_placeholder": "e.g. Genre: Experimental, Tempo: 95 BPM, Instrumentation: analog synths, field recordings...",
        "custom_style_help": "Define your own style with genre, tempo, instrumentation, etc.",
        "song_description": "📝 Song Description:",
        "song_desc_placeholder": "e.g. A melancholic song about lost love...",
        "song_desc_help": "Describe theme, mood or other wishes for your song",
        "generated_style": "🎼 Generated Style Description:",
        "create_song": "🚀 Create Song",
        "api_key_error": "❌ API Key not found! Please create .streamlit/secrets.toml and set suno_api_key = \"YOUR_KEY\".",
        "song_desc_required": "❌ Please describe your desired song!",
        "custom_style_required": "❌ Please define a custom style!",
        "generating_lyrics": "🧠 AI generating {genre} lyrics...",
        "analyzing_desc": "Analyzing your description and creating {genre} lyrics...",
        "lyrics_success": "✅ {genre} lyrics successfully generated!",
        "lyrics_error": "❌ Could not generate lyrics. Please try again.",
        "show_lyrics": "📝 Show Generated Lyrics",
        "lyrics_label": "Lyrics:",
        "style_label": "Style:",
        "creating_song": "🎵 Creating {genre} song...",
        "song_order_received": "🚀 {genre} song order received...",
        "song_generation_started": "✅ Song generation started",
        "api_error": "❌ API Error: {error}",
        "task_id_error": "❌ Could not extract Task ID",
        "timeout_error": "⏰ Timeout – Song could not be created in 10 minutes.",
        "connection_errors": "❌ Too many connection errors – Aborting.",
        "generation_failed": "❌ Song generation failed.",
        "no_audio_error": "❌ No audio file available.",
        "song_ready": "🎉 Your {genre} song is ready!",
        "title_metric": "🎵 Title",
        "genre_metric": "🎼 Genre",
        "duration_metric": "⏱️ Duration",
        "model_metric": "🤖 Model",
        "preparing_download": "Preparing download...",
        "download_song": "💾 Download {genre} song as MP3",
        "download_lyrics": "📝 Download {genre} lyrics as TXT",
        "download_both": "📦 Download Song + Lyrics",
        "download_song_with_lyrics": "💾 Download {genre} song + Lyrics",
        "download_only_lyrics": "📝 Only Lyrics",
        "download_all_files": "📦 Download All Files",
        "download_tip": "💡 Tip: When downloading the song, the lyrics are automatically provided as a separate file!",
        "song_created_success": "🎵 {genre} song successfully created! You can now download it.",
        "download_error": "❌ Download Error: {error}",
        "direct_link": "Direct Link: {url}",
        "credits_status": "💳 Credits Status",
        "remaining_credits": "Remaining Credits",
        "low_credits_warning": "⚠️ Few credits remaining!",
        "credits_running_low": "⚡ Credits running low",
        "sufficient_credits": "✅ Sufficient credits available",
        "credits_fetch_error": "❌ Could not fetch credits",
        "refresh_credits": "🔄 Refresh Credits",
        "api_provider": "🌐 API: sunoapi.org"
    },
    "de": {
        "app_title": "🤖 KI Song-Agent",
        "app_subtitle": "Dein persönlicher AI-Assistent für Songproduktion",
        "how_it_works": "🎵 Wie funktioniert der Song-Agent?",
        "how_it_works_desc": "Wähle ein Genre und beschreibe deinen Song - der Agent erstellt automatisch:",
        "features": [
            "📝 Professionelle Songtexte im richtigen Format",
            "🎼 Passende Stil- und Mood-Beschreibung basierend auf Genre",
            "🎧 Komplette MP3-Datei zum Download",
            "✨ Live-Anzeige der Stilbedeutung beim Genre-Wechsel"
        ],
        "new_feature": "Interaktive Genre-Auswahl mit Live-Stilvorschau!",
        "genre_selection": "🎼 Genre-Auswahl",
        "choose_genre": "Wähle ein Genre für automatische Stilgenerierung:",
        "live_style_preview": "🎯 Live-Stilvorschau",
        "song_config": "🎯 Song-Konfiguration",
        "selected_genre": "🎵 Gewähltes Genre:",
        "instrumental_only": "Nur instrumental",
        "custom_style_desc": "🎨 Benutzerdefinierte Stilbeschreibung:",
        "custom_style_placeholder": "z.B. Genre: Experimental, Tempo: 95 BPM, Instrumentation: analog synths, field recordings...",
        "custom_style_help": "Definiere deinen eigenen Stil mit Genre, Tempo, Instrumentierung, etc.",
        "song_description": "📝 Song-Beschreibung:",
        "song_desc_placeholder": "z.B. Ein melancholischer Song über verlorene Liebe...",
        "song_desc_help": "Beschreibe Thema, Stimmung oder andere Wünsche für deinen Song",
        "generated_style": "🎼 Generierte Stilbeschreibung:",
        "create_song": "🚀 Song erstellen",
        "api_key_error": "❌ API‑Key nicht gefunden! Bitte lege .streamlit/secrets.toml an und setze suno_api_key = \"DEIN_KEY\".",
        "song_desc_required": "❌ Bitte beschreibe deinen gewünschten Song!",
        "custom_style_required": "❌ Bitte definiere einen benutzerdefinierten Stil!",
        "generating_lyrics": "🧠 KI generiert {genre}-Songtexte...",
        "analyzing_desc": "Analysiere deine Beschreibung und erstelle {genre}-Songtexte...",
        "lyrics_success": "✅ {genre}-Songtexte erfolgreich generiert!",
        "lyrics_error": "❌ Konnte keine Songtexte generieren. Bitte versuche es erneut.",
        "show_lyrics": "📝 Generierte Songtexte anzeigen",
        "lyrics_label": "Lyrics:",
        "style_label": "Stil:",
        "creating_song": "🎵 {genre}-Song wird erstellt...",
        "song_order_received": "🚀 {genre}-Song Auftrag erhalten...",
        "song_generation_started": "✅ Song-Generierung gestartet",
        "api_error": "❌ API‑Fehler: {error}",
        "task_id_error": "❌ Konnte Task‑ID nicht extrahieren",
        "timeout_error": "⏰ Timeout – Song konnte nicht in 10 Minuten erstellt werden.",
        "connection_errors": "❌ Zu viele Verbindungsfehler – Abbruch.",
        "generation_failed": "❌ Song-Generierung fehlgeschlagen.",
        "no_audio_error": "❌ Keine Audio-Datei verfügbar.",
        "song_ready": "🎉 Dein {genre}-Song ist fertig!",
        "title_metric": "🎵 Titel",
        "genre_metric": "🎼 Genre",
        "duration_metric": "⏱️ Dauer",
        "model_metric": "🤖 Modell",
        "preparing_download": "Bereite Download vor...",
        "download_song": "💾 {genre}-Song als MP3 herunterladen",
        "download_lyrics": "📝 {genre}-Songtexte als TXT herunterladen",
        "download_both": "📦 Song + Songtexte herunterladen",
        "download_song_with_lyrics": "💾 {genre}-Song + Songtexte herunterladen",
        "download_only_lyrics": "📝 Nur Songtexte",
        "download_all_files": "📦 Alle Dateien herunterladen",
        "download_tip": "💡 Tipp: Beim Download des Songs werden automatisch auch die Songtexte als separate Datei bereitgestellt!",
        "song_created_success": "🎵 {genre}-Song erfolgreich erstellt! Du kannst ihn jetzt herunterladen.",
        "download_error": "❌ Download-Fehler: {error}",
        "direct_link": "Direkter Link: {url}",
        "credits_status": "💳 Credits-Status",
        "remaining_credits": "Verbleibende Credits",
        "low_credits_warning": "⚠️ Wenige Credits verbleibend!",
        "credits_running_low": "⚡ Credits werden knapp",
        "sufficient_credits": "✅ Ausreichend Credits verfügbar",
        "credits_fetch_error": "❌ Credits konnten nicht abgerufen werden",
        "refresh_credits": "🔄 Credits aktualisieren",
        "api_provider": "🌐 API: sunoapi.org"
    }
}

def get_text(key: str, **kwargs) -> str:
    """Get translated text for the current language"""
    lang = st.session_state.get('language', 'en')
    text = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

def init_language():
    """Initialize language in session state from config"""
    if 'language' not in st.session_state:
        st.session_state.language = get_saved_language()  # Load from config instead of default

# -------------------------------------------------------------------------
# 1) Konfiguration
# -------------------------------------------------------------------------
try:
    API_KEY = st.secrets["suno_api_key"]
except (KeyError, FileNotFoundError):
    st.error(get_text("api_key_error"))
    st.stop()

BASE_URL     = "https://api.sunoapi.org"
OLLAMA_URL   = "http://localhost:11434"  # Ollama Server URL
OLLAMA_MODEL = "gemma3n:e4b"             # Ollama Model
POLL_DELAY   = 5                         # Sekunden
TIMEOUT_HARD = 600                       # Abbruch nach 10 Minuten

# -------------------------------------------------------------------------
# 2) Genre-Stilbeschreibungen (Mehrsprachig)
# -------------------------------------------------------------------------
GENRE_STYLES = {
    "Deep House": {
        "tempo": "120-125 BPM",
        "instrumentation": {
            "en": "deep basslines, warm analog synths, subtle percussion, filtered vocals",
            "de": "tiefe Basslines, warme analoge Synths, subtile Percussion, gefilterte Vocals"
        },
        "vocals": {
            "en": "soulful vocals with reverb, occasional vocal chops",
            "de": "soulful Vocals mit Reverb, gelegentliche Vocal Chops"
        },
        "mood": {
            "en": "atmospheric, hypnotic, underground club vibes",
            "de": "atmosphärisch, hypnotisch, Underground Club-Vibes"
        },
        "description": {
            "en": "Deep House with warm basslines and atmospheric pads",
            "de": "Deep House mit warmen Basslines und atmosphärischen Pads"
        },
        "characteristics": {
            "en": [
                "🎵 Warm, deep basslines that carry the track",
                "🎹 Analog synthesizers with warm, round sounds", 
                "🥁 Subtle, minimalistic percussion elements",
                "🎤 Soulful vocals with lots of reverb and atmosphere",
                "🌊 Hypnotic, flowing arrangements",
                "🏠 Underground club atmosphere with depth"
            ],
            "de": [
                "🎵 Warme, tiefe Basslines die den Track tragen",
                "🎹 Analoge Synthesizer mit warmen, runden Klängen", 
                "🥁 Subtile, minimalistische Percussion-Elemente",
                "🎤 Soulful Vocals mit viel Reverb und Atmosphäre",
                "🌊 Hypnotische, fließende Arrangements",
                "🏠 Underground Club-Atmosphäre mit Tiefe"
            ]
        },
        "examples": {
            "en": "Artists like Kerri Chandler, Maya Jane Coles, Dixon",
            "de": "Künstler wie Kerri Chandler, Maya Jane Coles, Dixon"
        }
    },
    "Synthpop": {
        "tempo": "110-130 BPM", 
        "instrumentation": {
            "en": "vintage synthesizers, drum machines, arpeggiated sequences, bright leads",
            "de": "vintage Synthesizer, Drum Machines, arpeggierte Sequenzen, helle Leads"
        },
        "vocals": {
            "en": "clear melodic vocals, occasional vocoder effects",
            "de": "klare melodische Vocals, gelegentliche Vocoder-Effekte"
        },
        "mood": {
            "en": "nostalgic, uplifting, retro-futuristic",
            "de": "nostalgisch, uplifting, retro-futuristisch"
        },
        "description": {
            "en": "Synthpop with vintage synthesizers and nostalgic melodies",
            "de": "Synthpop mit vintage Synthesizern und nostalgischen Melodien"
        },
        "characteristics": {
            "en": [
                "🎹 Vintage synthesizers from the 80s (Moog, Roland)",
                "🥁 Classic drum machines (TR-808, LinnDrum)",
                "🎵 Arpeggiated sequences and catchy melodies",
                "✨ Bright, shining lead sounds",
                "🎤 Clear, melodic vocals with occasional vocoder effects",
                "🌈 Nostalgic, retro-futuristic atmosphere"
            ],
            "de": [
                "🎹 Vintage Synthesizer aus den 80ern (Moog, Roland)",
                "🥁 Klassische Drum Machines (TR-808, LinnDrum)",
                "🎵 Arpeggierte Sequenzen und eingängige Melodien",
                "✨ Helle, strahlende Lead-Sounds",
                "🎤 Klare, melodische Vocals mit gelegentlichen Vocoder-Effekten",
                "🌈 Nostalgische, retro-futuristische Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Depeche Mode, New Order, The Midnight",
            "de": "Künstler wie Depeche Mode, New Order, The Midnight"
        }
    },
    "Trap": {
        "tempo": "140-180 BPM",
        "instrumentation": {
            "en": "heavy 808 drums, hi-hats, dark synths, sub bass",
            "de": "schwere 808 Drums, Hi-Hats, dunkle Synths, Sub Bass"
        },
        "vocals": {
            "en": "rap vocals with autotune, ad-libs, vocal chops",
            "de": "Rap-Vocals mit Auto-Tune, Ad-Libs, Vocal Chops"
        },
        "mood": {
            "en": "aggressive, dark, street energy",
            "de": "aggressiv, dunkel, Street-Energy"
        },
        "description": {
            "en": "Trap with heavy 808s and dark synths",
            "de": "Trap mit schweren 808s und dunklen Synths"
        },
        "characteristics": {
            "en": [
                "🥁 Heavy 808 drums as rhythmic foundation",
                "⚡ Fast, rolling hi-hat patterns",
                "🎹 Dark, aggressive synthesizer sounds",
                "🔊 Deep sub bass for maximum impact",
                "🎤 Rap vocals with auto-tune and ad-libs",
                "🌃 Dark, urban street atmosphere"
            ],
            "de": [
                "🥁 Schwere 808-Drums als rhythmische Basis",
                "⚡ Schnelle, rollende Hi-Hat-Patterns",
                "🎹 Dunkle, aggressive Synthesizer-Sounds",
                "🔊 Tiefer Sub-Bass für maximalen Impact",
                "🎤 Rap-Vocals mit Auto-Tune und Ad-Libs",
                "🌃 Düstere, urbane Street-Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Travis Scott, Future, Metro Boomin",
            "de": "Künstler wie Travis Scott, Future, Metro Boomin"
        }
    },
    "Techno": {
        "tempo": "125-135 BPM",
        "instrumentation": {
            "en": "four-on-the-floor kick, industrial sounds, acid synths, minimal percussion",
            "de": "Four-on-the-floor Kick, industrielle Sounds, Acid Synths, minimale Percussion"
        },
        "vocals": {
            "en": "minimal vocals, robotic effects, vocal stabs",
            "de": "minimale Vocals, robotische Effekte, Vocal Stabs"
        },
        "mood": {
            "en": "driving, hypnotic, industrial atmosphere",
            "de": "treibend, hypnotisch, industrielle Atmosphäre"
        },
        "description": {
            "en": "Techno with driving beats and industrial sounds",
            "de": "Techno mit treibenden Beats und industriellen Klängen"
        },
        "characteristics": {
            "en": [
                "🥁 Four-on-the-floor kick pattern as foundation",
                "🏭 Industrial sounds and mechanical elements",
                "🎹 Acid synthesizers with characteristic sweeps",
                "⚙️ Minimalistic, precise percussion",
                "🤖 Robotic vocal effects and stabs",
                "🌀 Hypnotic, driving energy"
            ],
            "de": [
                "🥁 Four-on-the-floor Kick-Pattern als Grundlage",
                "🏭 Industrielle Sounds und mechanische Elemente",
                "🎹 Acid-Synthesizer mit charakteristischen Sweeps",
                "⚙️ Minimalistische, präzise Percussion",
                "🤖 Robotische Vocal-Effekte und Stabs",
                "🌀 Hypnotische, treibende Energie"
            ]
        },
        "examples": {
            "en": "Artists like Carl Cox, Charlotte de Witte, Amelie Lens",
            "de": "Künstler wie Carl Cox, Charlotte de Witte, Amelie Lens"
        }
    },
    "Ambient": {
        "tempo": "60-90 BPM",
        "instrumentation": {
            "en": "atmospheric pads, field recordings, reverb-heavy textures, minimal percussion",
            "de": "atmosphärische Pads, Field Recordings, Reverb-lastige Texturen, minimale Percussion"
        },
        "vocals": {
            "en": "ethereal vocals, whispered elements, vocal textures",
            "de": "ätherische Vocals, geflüsterte Elemente, Vocal-Texturen"
        },
        "mood": {
            "en": "meditative, spacious, contemplative",
            "de": "meditativ, weiträumig, kontemplativ"
        },
        "description": {
            "en": "Ambient with atmospheric textures and meditative sounds",
            "de": "Ambient mit atmosphärischen Texturen und meditativen Klängen"
        },
        "characteristics": {
            "en": [
                "🌌 Atmospheric pads and textures",
                "🎙️ Field recordings from nature",
                "💫 Reverb-heavy, space-filling sounds",
                "🥁 Minimal or no percussion",
                "👻 Ethereal, whispered vocal elements",
                "🧘 Meditative, contemplative mood"
            ],
            "de": [
                "🌌 Atmosphärische Pads und Texturen",
                "🎙️ Field Recordings aus der Natur",
                "💫 Reverb-lastige, raumfüllende Sounds",
                "🥁 Minimale oder keine Percussion",
                "👻 Ätherische, geflüsterte Vocal-Elemente",
                "🧘 Meditative, kontemplative Stimmung"
            ]
        },
        "examples": {
            "en": "Artists like Brian Eno, Stars of the Lid, Tim Hecker",
            "de": "Künstler wie Brian Eno, Stars of the Lid, Tim Hecker"
        }
    },
    "Drum & Bass": {
        "tempo": "170-180 BPM",
        "instrumentation": {
            "en": "fast breakbeats, heavy sub bass, jungle samples, synthesized leads",
            "de": "schnelle Breakbeats, schwerer Sub Bass, Jungle Samples, synthetisierte Leads"
        },
        "vocals": {
            "en": "chopped vocal samples, MC vocals, ragga influences",
            "de": "gehackte Vocal Samples, MC Vocals, Ragga-Einflüsse"
        },
        "mood": {
            "en": "energetic, fast-paced, underground rave energy",
            "de": "energetisch, schnell, Underground Rave-Energy"
        },
        "description": {
            "en": "Drum & Bass with fast breakbeats and heavy sub bass",
            "de": "Drum & Bass mit schnellen Breakbeats und schwerem Sub-Bass"
        },
        "characteristics": {
            "en": [
                "🥁 Fast, complex breakbeat patterns",
                "🔊 Heavy, dominant sub bass",
                "🌿 Jungle samples and breaks",
                "🎹 Synthesized leads and stabs",
                "🎤 Chopped vocal samples and MC vocals",
                "⚡ High-energy underground rave atmosphere"
            ],
            "de": [
                "🥁 Schnelle, komplexe Breakbeat-Patterns",
                "🔊 Schwerer, dominanter Sub-Bass",
                "🌿 Jungle-Samples und Breaks",
                "🎹 Synthesized Leads und Stabs",
                "🎤 Gehackte Vocal-Samples und MC-Vocals",
                "⚡ Hochenergetische Underground-Rave-Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like LTJ Bukem, Goldie, Netsky",
            "de": "Künstler wie LTJ Bukem, Goldie, Netsky"
        }
    },
    "Future Bass": {
        "tempo": "130-160 BPM",
        "instrumentation": {
            "en": "pitched vocal chops, supersaws, trap-influenced drums, melodic drops",
            "de": "gepitchte Vocal Chops, Supersaws, Trap-beeinflusste Drums, melodische Drops"
        },
        "vocals": {
            "en": "pitched vocal samples, emotional singing, vocal chops",
            "de": "gepitchte Vocal Samples, emotionaler Gesang, Vocal Chops"
        },
        "mood": {
            "en": "emotional, uplifting, festival energy",
            "de": "emotional, uplifting, Festival-Energy"
        },
        "description": {
            "en": "Future Bass with emotional vocal chops and melodic drops",
            "de": "Future Bass mit emotionalen Vocal Chops und melodischen Drops"
        },
        "characteristics": {
            "en": [
                "🎤 Pitched vocal chops as main element",
                "🎹 Supersaw synthesizers for wide sounds",
                "🥁 Trap-influenced drum patterns",
                "💫 Melodic, emotional drops",
                "❤️ Emotional, uplifting mood",
                "🎪 Festival-ready energy and euphoria"
            ],
            "de": [
                "🎤 Gepitchte Vocal Chops als Hauptelement",
                "🎹 Supersaw-Synthesizer für breite Sounds",
                "🥁 Trap-beeinflusste Drum-Patterns",
                "💫 Melodische, emotionale Drops",
                "❤️ Gefühlvolle, uplifting Stimmung",
                "🎪 Festival-taugliche Energie und Euphorie"
            ]
        },
        "examples": {
            "en": "Artists like Flume, Illenium, San Holo",
            "de": "Künstler wie Flume, Illenium, San Holo"
        }
    },
    "Lo-Fi Hip Hop": {
        "tempo": "70-90 BPM",
        "instrumentation": {
            "en": "vinyl crackle, jazz samples, muted drums, warm bass",
            "de": "Vinyl-Knistern, Jazz Samples, gedämpfte Drums, warmer Bass"
        },
        "vocals": {
            "en": "minimal vocals, spoken word, jazz vocal samples",
            "de": "minimale Vocals, Spoken Word, Jazz Vocal Samples"
        },
        "mood": {
            "en": "relaxed, nostalgic, study vibes",
            "de": "entspannt, nostalgisch, Study-Vibes"
        },
        "description": {
            "en": "Lo-Fi Hip Hop with jazz samples and relaxed beats",
            "de": "Lo-Fi Hip Hop mit Jazz-Samples und entspannten Beats"
        },
        "characteristics": {
            "en": [
                "📀 Vinyl crackle and lo-fi texture",
                "🎷 Jazz samples and warm instruments",
                "🥁 Muted, relaxed drum patterns",
                "🎸 Warm, round bass sound",
                "🎤 Minimal vocals or spoken word",
                "☕ Nostalgic study and chill vibes"
            ],
            "de": [
                "📀 Vinyl-Knistern und Lo-Fi-Textur",
                "🎷 Jazz-Samples und warme Instrumente",
                "🥁 Gedämpfte, entspannte Drum-Patterns",
                "🎸 Warmer, runder Bass-Sound",
                "🎤 Minimale Vocals oder Spoken Word",
                "☕ Nostalgische Study- und Chill-Vibes"
            ]
        },
        "examples": {
            "en": "Artists like Nujabes, J Dilla, ChilledCow",
            "de": "Künstler wie Nujabes, J Dilla, ChilledCow"
        }
    },
    "Psytrance": {
        "tempo": "140-150 BPM",
        "instrumentation": {
            "en": "psychedelic leads, rolling basslines, tribal percussion, acid sequences",
            "de": "psychedelische Leads, rollende Basslines, tribale Percussion, Acid-Sequenzen"
        },
        "vocals": {
            "en": "minimal vocals, psychedelic effects, vocal samples",
            "de": "minimale Vocals, psychedelische Effekte, Vocal Samples"
        },
        "mood": {
            "en": "psychedelic, trance-inducing, festival energy",
            "de": "psychedelisch, trance-induzierend, Festival-Energy"
        },
        "description": {
            "en": "Psytrance with psychedelic leads and driving basslines",
            "de": "Psytrance mit psychedelischen Leads und treibenden Basslines"
        },
        "characteristics": {
            "en": [
                "🌀 Psychedelic, distorted lead sounds",
                "🎵 Rolling, hypnotic basslines",
                "🥁 Tribal-influenced percussion elements",
                "🧪 Acid sequences and experimental sounds",
                "👽 Minimal vocals with psychedelic effects",
                "🎪 Trance-inducing festival energy"
            ],
            "de": [
                "🌀 Psychedelische, verzerrte Lead-Sounds",
                "🎵 Rollende, hypnotische Basslines",
                "🥁 Tribal-beeinflusste Percussion-Elemente",
                "🧪 Acid-Sequenzen und experimentelle Sounds",
                "👽 Minimale Vocals mit psychedelischen Effekten",
                "🎪 Trance-induzierende Festival-Energie"
            ]
        },
        "examples": {
            "en": "Artists like Infected Mushroom, Astrix, Vini Vici",
            "de": "Künstler wie Infected Mushroom, Astrix, Vini Vici"
        }
    },
    "Indie Pop": {
        "tempo": "100-120 BPM",
        "instrumentation": {
            "en": "jangly guitars, indie drums, vintage keyboards, melodic bass",
            "de": "jangly Gitarren, Indie Drums, Vintage Keyboards, melodischer Bass"
        },
        "vocals": {
            "en": "indie vocals with character, harmonies, emotional delivery",
            "de": "Indie Vocals mit Charakter, Harmonien, emotionale Darbietung"
        },
        "mood": {
            "en": "dreamy, nostalgic, alternative vibes",
            "de": "träumerisch, nostalgisch, Alternative-Vibes"
        },
        "description": {
            "en": "Indie Pop with jangly guitars and dreamy melodies",
            "de": "Indie Pop mit jangly Gitarren und träumerischen Melodien"
        },
        "characteristics": {
            "en": [
                "🎸 Jangly, characteristic guitar sounds",
                "🥁 Indie-typical, organic drum patterns",
                "🎹 Vintage keyboards and warm sounds",
                "🎵 Melodic, catchy basslines",
                "🎤 Characteristic indie vocals with harmonies",
                "💭 Dreamy, nostalgic alternative vibes"
            ],
            "de": [
                "🎸 Jangly, charakteristische Gitarren-Sounds",
                "🥁 Indie-typische, organische Drum-Patterns",
                "🎹 Vintage Keyboards und warme Sounds",
                "🎵 Melodische, eingängige Basslines",
                "🎤 Charaktervolle Indie-Vocals mit Harmonien",
                "💭 Träumerische, nostalgische Alternative-Vibes"
            ]
        },
        "examples": {
            "en": "Artists like Arctic Monkeys, Tame Impala, The Strokes",
            "de": "Künstler wie Arctic Monkeys, Tame Impala, The Strokes"
        }
    },
    "Hardstyle": {
        "tempo": "150-160 BPM",
        "instrumentation": {
            "en": "hard kicks, euphoric leads, reverse bass, hardcore elements",
            "de": "harte Kicks, euphorische Leads, Reverse Bass, Hardcore-Elemente"
        },
        "vocals": {
            "en": "powerful vocals, hardcore shouts, emotional breakdowns",
            "de": "kraftvolle Vocals, Hardcore-Shouts, emotionale Breakdowns"
        },
        "mood": {
            "en": "euphoric, hard, festival anthem energy",
            "de": "euphorisch, hart, Festival-Anthem-Energy"
        },
        "description": {
            "en": "Hardstyle with hard kicks and euphoric leads",
            "de": "Hardstyle mit harten Kicks und euphorischen Leads"
        },
        "characteristics": {
            "en": [
                "🥁 Hard, distorted kick drums",
                "🎹 Euphoric, emotional lead melodies",
                "🔄 Reverse bass and characteristic sounds",
                "⚡ Hardcore elements and hard breaks",
                "🎤 Powerful vocals and hardcore shouts",
                "🎪 Festival anthem energy and euphoria"
            ],
            "de": [
                "🥁 Harte, verzerrte Kick-Drums",
                "🎹 Euphorische, emotionale Lead-Melodien",
                "🔄 Reverse Bass und charakteristische Sounds",
                "⚡ Hardcore-Elemente und harte Breaks",
                "🎤 Kraftvolle Vocals und Hardcore-Shouts",
                "🎪 Festival-Anthem-Energie und Euphorie"
            ]
        },
        "examples": {
            "en": "Artists like Headhunterz, Brennan Heart, Da Tweekaz",
            "de": "Künstler wie Headhunterz, Brennan Heart, Da Tweekaz"
        }
    },
    "Reggaeton": {
        "tempo": "90-100 BPM",
        "instrumentation": {
            "en": "dembow rhythm, latin percussion, reggaeton drums, tropical elements",
            "de": "Dembow-Rhythmus, lateinamerikanische Percussion, Reggaeton Drums, tropische Elemente"
        },
        "vocals": {
            "en": "spanish rap vocals, melodic hooks, latin influences",
            "de": "spanische Rap-Vocals, melodische Hooks, lateinamerikanische Einflüsse"
        },
        "mood": {
            "en": "party vibes, latin energy, danceable",
            "de": "Party-Vibes, lateinamerikanische Energy, tanzbar"
        },
        "description": {
            "en": "Reggaeton with dembow rhythm and latin influences",
            "de": "Reggaeton mit Dembow-Rhythmus und lateinamerikanischen Einflüssen"
        },
        "characteristics": {
            "en": [
                "🥁 Characteristic dembow rhythm",
                "🎵 Latin percussion elements",
                "🌴 Tropical sounds and instruments",
                "🎤 Spanish rap vocals and melodic hooks",
                "💃 Danceable, party-ready energy",
                "🌶️ Latin culture and vibes"
            ],
            "de": [
                "🥁 Charakteristischer Dembow-Rhythmus",
                "🎵 Lateinamerikanische Percussion-Elemente",
                "🌴 Tropische Sounds und Instrumente",
                "🎤 Spanische Rap-Vocals und melodische Hooks",
                "💃 Tanzbare, party-taugliche Energie",
                "🌶️ Lateinamerikanische Kultur und Vibes"
            ]
        },
        "examples": {
            "en": "Artists like Bad Bunny, J Balvin, Daddy Yankee",
            "de": "Künstler wie Bad Bunny, J Balvin, Daddy Yankee"
        }
    },
    "Piano Ballad": {
        "tempo": "60-80 BPM",
        "instrumentation": {
            "en": "grand piano, strings, subtle percussion, orchestral elements",
            "de": "Flügel, Streicher, subtile Percussion, orchestrale Elemente"
        },
        "vocals": {
            "en": "emotional vocals, powerful delivery, intimate moments",
            "de": "emotionale Vocals, kraftvolle Darbietung, intime Momente"
        },
        "mood": {
            "en": "emotional, intimate, heartfelt",
            "de": "emotional, intim, herzlich"
        },
        "description": {
            "en": "Piano ballad with emotional vocals and orchestral elements",
            "de": "Piano Ballade mit emotionalen Vocals und orchestralen Elementen"
        },
        "characteristics": {
            "en": [
                "🎹 Grand piano as main instrument",
                "🎻 Warm string arrangements",
                "🥁 Subtle, supporting percussion",
                "🎼 Orchestral elements for drama",
                "🎤 Emotional, powerful vocals",
                "💝 Intimate, heartfelt atmosphere"
            ],
            "de": [
                "🎹 Großartiges Klavier als Hauptinstrument",
                "🎻 Warme Streicher-Arrangements",
                "🥁 Subtile, unterstützende Percussion",
                "🎼 Orchestrale Elemente für Dramatik",
                "🎤 Emotionale, kraftvolle Vocals",
                "💝 Intime, herzliche Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Adele, John Legend, Alicia Keys",
            "de": "Künstler wie Adele, John Legend, Alicia Keys"
        }
    },
    "Emotional": {
        "tempo": "70-100 BPM",
        "instrumentation": {
            "en": "piano, acoustic guitar, strings, soft drums, ambient pads",
            "de": "Klavier, akustische Gitarre, Streicher, sanfte Drums, Ambient Pads"
        },
        "vocals": {
            "en": "vulnerable vocals, emotional delivery, harmonies",
            "de": "verletzliche Vocals, emotionale Darbietung, Harmonien"
        },
        "mood": {
            "en": "emotional, vulnerable, touching",
            "de": "emotional, verletzlich, berührend"
        },
        "description": {
            "en": "Emotional music with vulnerable vocals and warm instruments",
            "de": "Emotionale Musik mit verletzlichen Vocals und warmen Instrumenten"
        },
        "characteristics": {
            "en": [
                "🎹 Warm piano for emotional depth",
                "🎸 Acoustic guitar with gentle tones",
                "🎻 Emotional string arrangements",
                "🥁 Soft, supporting drums",
                "🎤 Vulnerable, touching vocals",
                "💔 Deep emotional connection"
            ],
            "de": [
                "🎹 Warmes Klavier für emotionale Tiefe",
                "🎸 Akustische Gitarre mit sanften Tönen",
                "🎻 Emotionale Streicher-Arrangements",
                "🥁 Sanfte, unterstützende Drums",
                "🎤 Verletzliche, berührende Vocals",
                "💔 Tiefe emotionale Verbindung"
            ]
        },
        "examples": {
            "en": "Artists like Bon Iver, Phoebe Bridgers, Sufjan Stevens",
            "de": "Künstler wie Bon Iver, Phoebe Bridgers, Sufjan Stevens"
        }
    },
    "Romantic": {
        "tempo": "80-110 BPM",
        "instrumentation": {
            "en": "acoustic guitar, piano, strings, soft percussion, warm bass",
            "de": "akustische Gitarre, Klavier, Streicher, sanfte Percussion, warmer Bass"
        },
        "vocals": {
            "en": "tender vocals, romantic delivery, sweet harmonies",
            "de": "zärtliche Vocals, romantische Darbietung, süße Harmonien"
        },
        "mood": {
            "en": "romantic, tender, loving",
            "de": "romantisch, zärtlich, liebevoll"
        },
        "description": {
            "en": "Romantic music with tender vocals and warm arrangements",
            "de": "Romantische Musik mit zärtlichen Vocals und warmen Arrangements"
        },
        "characteristics": {
            "en": [
                "🎸 Gentle acoustic guitar",
                "🎹 Romantic piano playing",
                "🎻 Loving string arrangements",
                "🥁 Tender, rhythmic percussion",
                "🎤 Tender, romantic vocals",
                "💕 Loving, warm atmosphere"
            ],
            "de": [
                "🎸 Sanfte akustische Gitarre",
                "🎹 Romantisches Klavier-Spiel",
                "🎻 Liebevolle Streicher-Arrangements",
                "🥁 Zarte, rhythmische Percussion",
                "🎤 Zärtliche, romantische Vocals",
                "💕 Liebevolle, warme Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Ed Sheeran, John Mayer, Norah Jones",
            "de": "Künstler wie Ed Sheeran, John Mayer, Norah Jones"
        }
    },
    "Acoustic": {
        "tempo": "90-120 BPM",
        "instrumentation": {
            "en": "acoustic guitar, light percussion, harmonica, mandolin, natural sounds",
            "de": "akustische Gitarre, leichte Percussion, Harmonika, Mandoline, natürliche Sounds"
        },
        "vocals": {
            "en": "natural vocals, storytelling, harmonies",
            "de": "natürliche Vocals, Storytelling, Harmonien"
        },
        "mood": {
            "en": "organic, natural, authentic",
            "de": "organisch, natürlich, authentisch"
        },
        "description": {
            "en": "Acoustic music with natural instruments and authentic vocals",
            "de": "Akustische Musik mit natürlichen Instrumenten und authentischen Vocals"
        },
        "characteristics": {
            "en": [
                "🎸 Acoustic guitar as main instrument",
                "🥁 Light, organic percussion",
                "🎵 Harmonica and mandolin",
                "🌿 Natural, unprocessed sounds",
                "🎤 Authentic, storytelling vocals",
                "🏞️ Organic, earthy atmosphere"
            ],
            "de": [
                "🎸 Akustische Gitarre als Hauptinstrument",
                "🥁 Leichte, organische Percussion",
                "🎵 Harmonika und Mandoline",
                "🌿 Natürliche, unverarbeitete Sounds",
                "🎤 Authentische, erzählende Vocals",
                "🏞️ Organische, erdige Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Jack Johnson, Damien Rice, Iron & Wine",
            "de": "Künstler wie Jack Johnson, Damien Rice, Iron & Wine"
        }
    },
    "Jazz": {
        "tempo": "100-140 BPM",
        "instrumentation": {
            "en": "piano, upright bass, drums, brass section, saxophone",
            "de": "Klavier, Kontrabass, Drums, Bläser-Sektion, Saxophon"
        },
        "vocals": {
            "en": "smooth jazz vocals, scatting, improvisation",
            "de": "smooth Jazz-Vocals, Scatting, Improvisation"
        },
        "mood": {
            "en": "sophisticated, smooth, improvisational",
            "de": "sophisticated, smooth, improvisiert"
        },
        "description": {
            "en": "Jazz with improvised elements and sophisticated harmonies",
            "de": "Jazz mit improvisierten Elementen und sophistizierten Harmonien"
        },
        "characteristics": {
            "en": [
                "🎹 Virtuoso jazz piano",
                "🎸 Upright bass with walking bass",
                "🥁 Swing rhythms and brushes",
                "🎺 Brass section and saxophones",
                "🎤 Smooth jazz vocals with scatting",
                "🎭 Sophisticated, improvised atmosphere"
            ],
            "de": [
                "🎹 Virtuoses Jazz-Piano",
                "🎸 Kontrabass mit Walking Bass",
                "🥁 Swing-Rhythmen und Brushes",
                "🎺 Brass-Sektion und Saxophone",
                "🎤 Smooth Jazz-Vocals mit Scatting",
                "🎭 Sophisticated, improvisierte Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Ella Fitzgerald, Miles Davis, Norah Jones",
            "de": "Künstler wie Ella Fitzgerald, Miles Davis, Norah Jones"
        }
    },
    "Classical": {
        "tempo": "Variable",
        "instrumentation": {
            "en": "full orchestra, piano, strings, woodwinds, brass",
            "de": "vollständiges Orchester, Klavier, Streicher, Holzbläser, Blechbläser"
        },
        "vocals": {
            "en": "operatic vocals, choir, classical technique",
            "de": "operatische Vocals, Chor, klassische Technik"
        },
        "mood": {
            "en": "elegant, dramatic, timeless",
            "de": "elegant, dramatisch, zeitlos"
        },
        "description": {
            "en": "Classical music with orchestral arrangements and timeless elegance",
            "de": "Klassische Musik mit orchestralen Arrangements und zeitloser Eleganz"
        },
        "characteristics": {
            "en": [
                "🎼 Full orchestra arrangement",
                "🎹 Concert piano as solo instrument",
                "🎻 Rich string section",
                "🎺 Wind section with woodwinds and brass",
                "🎤 Operatic vocals or choir",
                "👑 Elegant, timeless atmosphere"
            ],
            "de": [
                "🎼 Vollständiges Orchester-Arrangement",
                "🎹 Konzert-Klavier als Soloinstrument",
                "🎻 Reiche Streicher-Sektion",
                "🎺 Bläser-Sektion mit Holz und Blech",
                "🎤 Operatische Vocals oder Chor",
                "👑 Elegante, zeitlose Atmosphäre"
            ]
        },
        "examples": {
            "en": "Composers like Mozart, Beethoven, modern crossover artists",
            "de": "Komponisten wie Mozart, Beethoven, moderne Crossover-Künstler"
        }
    },
    "R&B": {
        "tempo": "70-110 BPM",
        "instrumentation": {
            "en": "electric piano, bass guitar, drums, horn section, smooth synths",
            "de": "Electric Piano, Bass Guitar, Drums, Horn-Sektion, smooth Synths"
        },
        "vocals": {
            "en": "soulful R&B vocals, melismatic runs, harmonies",
            "de": "soulful R&B-Vocals, melismatische Läufe, Harmonien"
        },
        "mood": {
            "en": "smooth, soulful, groove-oriented",
            "de": "smooth, soulful, groove-orientiert"
        },
        "description": {
            "en": "R&B with soulful vocals and groove-oriented rhythms",
            "de": "R&B mit soulful Vocals und groove-orientierten Rhythmen"
        },
        "characteristics": {
            "en": [
                "🎹 Electric piano and warm keys",
                "🎸 Groove-oriented bass guitar",
                "🥁 Tight R&B drum patterns",
                "🎺 Horn section for punch",
                "🎤 Soulful vocals with melismas",
                "🌟 Smooth, groove-based atmosphere"
            ],
            "de": [
                "🎹 Electric Piano und warme Keys",
                "🎸 Groove-orientierte Bass-Guitar",
                "🥁 Tight R&B-Drum-Patterns",
                "🎺 Horn-Sektion für Punch",
                "🎤 Soulful Vocals mit Melismen",
                "🌟 Smooth, groove-basierte Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Alicia Keys, John Legend, The Weeknd",
            "de": "Künstler wie Alicia Keys, John Legend, The Weeknd"
        }
    },
    "Soul": {
        "tempo": "80-120 BPM",
        "instrumentation": {
            "en": "organ, bass guitar, drums, horn section, gospel piano",
            "de": "Orgel, Bass Guitar, Drums, Horn-Sektion, Gospel Piano"
        },
        "vocals": {
            "en": "powerful soul vocals, gospel influences, call and response",
            "de": "kraftvolle Soul-Vocals, Gospel-Einflüsse, Call and Response"
        },
        "mood": {
            "en": "passionate, spiritual, uplifting",
            "de": "leidenschaftlich, spirituell, uplifting"
        },
        "description": {
            "en": "Soul with powerful vocals and gospel-inspired arrangements",
            "de": "Soul mit kraftvollen Vocals und gospel-inspirierten Arrangements"
        },
        "characteristics": {
            "en": [
                "🎹 Hammond organ and gospel piano",
                "🎸 Funky bass guitar grooves",
                "🥁 Powerful soul drum patterns",
                "🎺 Punchy horn arrangements",
                "🎤 Powerful soul vocals with gospel influences",
                "⛪ Spiritual, uplifting atmosphere"
            ],
            "de": [
                "🎹 Hammond-Orgel und Gospel-Piano",
                "🎸 Funky Bass-Guitar-Grooves",
                "🥁 Kraftvolle Soul-Drum-Patterns",
                "🎺 Punchy Horn-Arrangements",
                "🎤 Kraftvolle Soul-Vocals mit Gospel-Einflüssen",
                "⛪ Spirituelle, uplifting Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Aretha Franklin, Stevie Wonder, Amy Winehouse",
            "de": "Künstler wie Aretha Franklin, Stevie Wonder, Amy Winehouse"
        }
    },
    "Country": {
        "tempo": "90-130 BPM",
        "instrumentation": {
            "en": "acoustic guitar, banjo, fiddle, steel guitar, harmonica",
            "de": "akustische Gitarre, Banjo, Fiddle, Steel Guitar, Harmonika"
        },
        "vocals": {
            "en": "country vocals, storytelling, twang",
            "de": "Country-Vocals, Storytelling, Twang"
        },
        "mood": {
            "en": "authentic, storytelling, down-to-earth",
            "de": "authentisch, erzählend, bodenständig"
        },
        "description": {
            "en": "Country with authentic instruments and storytelling vocals",
            "de": "Country mit authentischen Instrumenten und erzählenden Vocals"
        },
        "characteristics": {
            "en": [
                "🎸 Acoustic and steel guitar",
                "🪕 Banjo for authentic sound",
                "🎻 Fiddle for melodic elements",
                "🎵 Harmonica for atmosphere",
                "🎤 Storytelling country vocals with twang",
                "🤠 Authentic, down-to-earth atmosphere"
            ],
            "de": [
                "🎸 Akustische und Steel-Gitarre",
                "🪕 Banjo für authentischen Sound",
                "🎻 Fiddle für melodische Elemente",
                "🎵 Harmonika für Atmosphäre",
                "🎤 Erzählende Country-Vocals mit Twang",
                "🤠 Authentische, bodenständige Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Johnny Cash, Dolly Parton, Chris Stapleton",
            "de": "Künstler wie Johnny Cash, Dolly Parton, Chris Stapleton"
        }
    },
    "Folk": {
        "tempo": "80-110 BPM",
        "instrumentation": {
            "en": "acoustic guitar, harmonica, banjo, mandolin, simple percussion",
            "de": "akustische Gitarre, Harmonika, Banjo, Mandoline, einfache Percussion"
        },
        "vocals": {
            "en": "natural folk vocals, storytelling, harmonies",
            "de": "natürliche Folk-Vocals, Storytelling, Harmonien"
        },
        "mood": {
            "en": "authentic, traditional, narrative",
            "de": "authentisch, traditionell, narrativ"
        },
        "description": {
            "en": "Folk with traditional instruments and storytelling vocals",
            "de": "Folk mit traditionellen Instrumenten und erzählenden Vocals"
        },
        "characteristics": {
            "en": [
                "🎸 Acoustic guitar as foundation",
                "🎵 Harmonica for melody",
                "🪕 Banjo and mandolin",
                "🥁 Simple, natural percussion",
                "🎤 Authentic folk vocals with stories",
                "📚 Traditional, narrative atmosphere"
            ],
            "de": [
                "🎸 Akustische Gitarre als Basis",
                "🎵 Harmonika für Melodie",
                "🪕 Banjo und Mandoline",
                "🥁 Einfache, natürliche Percussion",
                "🎤 Authentische Folk-Vocals mit Geschichten",
                "📚 Traditionelle, narrative Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Bob Dylan, Joni Mitchell, Fleet Foxes",
            "de": "Künstler wie Bob Dylan, Joni Mitchell, Fleet Foxes"
        }
    },
    "Pop Rock": {
        "tempo": "110-140 BPM",
        "instrumentation": {
            "en": "electric guitar, bass guitar, drums, keyboards, catchy hooks",
            "de": "Electric Guitar, Bass Guitar, Drums, Keyboards, eingängige Hooks"
        },
        "vocals": {
            "en": "pop vocals, anthemic choruses, harmonies",
            "de": "Pop-Vocals, anthemische Choruses, Harmonien"
        },
        "mood": {
            "en": "energetic, catchy, mainstream appeal",
            "de": "energetisch, eingängig, Mainstream-Appeal"
        },
        "description": {
            "en": "Pop Rock with catchy hooks and anthemic choruses",
            "de": "Pop Rock mit eingängigen Hooks und anthemischen Choruses"
        },
        "characteristics": {
            "en": [
                "🎸 Catchy electric guitar riffs",
                "🎸 Powerful bass guitar",
                "🥁 Driving rock drum patterns",
                "🎹 Supporting keyboards",
                "🎤 Catchy pop vocals",
                "🎪 Energetic, mainstream-ready atmosphere"
            ],
            "de": [
                "🎸 Eingängige Electric-Guitar-Riffs",
                "🎸 Kraftvolle Bass-Guitar",
                "🥁 Treibende Rock-Drum-Patterns",
                "🎹 Unterstützende Keyboards",
                "🎤 Eingängige Pop-Vocals",
                "🎪 Energetische, mainstream-taugliche Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Maroon 5, OneRepublic, Imagine Dragons",
            "de": "Künstler wie Maroon 5, OneRepublic, Imagine Dragons"
        }
    },
    "Alternative Rock": {
        "tempo": "100-130 BPM",
        "instrumentation": {
            "en": "distorted guitars, bass guitar, drums, experimental elements",
            "de": "verzerrte Gitarren, Bass Guitar, Drums, experimentelle Elemente"
        },
        "vocals": {
            "en": "alternative vocals, emotional delivery, raw energy",
            "de": "Alternative-Vocals, emotionale Darbietung, rohe Energie"
        },
        "mood": {
            "en": "alternative, edgy, authentic",
            "de": "alternativ, kantig, authentisch"
        },
        "description": {
            "en": "Alternative Rock with distorted guitars and authentic energy",
            "de": "Alternative Rock mit verzerrten Gitarren und authentischer Energie"
        },
        "characteristics": {
            "en": [
                "🎸 Distorted, characteristic guitars",
                "🎸 Powerful, rhythmic bass guitar",
                "🥁 Alternative drum patterns",
                "🔧 Experimental sound elements",
                "🎤 Authentic alternative vocals",
                "⚡ Edgy, unconventional atmosphere"
            ],
            "de": [
                "🎸 Verzerrte, charakteristische Gitarren",
                "🎸 Kraftvolle, rhythmische Bass-Guitar",
                "🥁 Alternative Drum-Patterns",
                "🔧 Experimentelle Sound-Elemente",
                "🎤 Authentische Alternative-Vocals",
                "⚡ Edgy, unkonventionelle Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Radiohead, Foo Fighters, Pearl Jam",
            "de": "Künstler wie Radiohead, Foo Fighters, Pearl Jam"
        }
    },
    "Alternative Metal": {
        "tempo": "90-140 BPM",
        "instrumentation": {
            "en": "distorted guitars, heavy drums, bass, often with orchestral and electronic elements",
            "de": "verzerrte Gitarren, harte Drums, Bass, oft mit orchestralen und elektronischen Elementen"
        },
        "vocals": {
            "en": "melodic vocals alternating with intense screaming",
            "de": "melodischer Gesang wechselt sich mit intensivem Schreien (Screaming) ab"
        },
        "mood": {
            "en": "emotional, powerful, dramatic, often dark",
            "de": "emotional, kraftvoll, dramatisch, oft düster"
        },
        "description": {
            "en": "Alternative Metal with a mix of heavy riffs and emotional melodies",
            "de": "Alternative Metal mit einer Mischung aus harten Riffs und emotionalen Melodien"
        },
        "characteristics": {
            "en": [
                "🎸 Heavy, distorted guitar riffs",
                "🥁 Powerful and precise drum patterns",
                "🎻 Use of orchestral elements like strings and piano",
                "🎤 Dynamic vocals switching between clear melodies and shouts/screams",
                "🎹 Integration of electronic sounds and synthesizers",
                "🎭 Dramatic and emotional song structures"
            ],
            "de": [
                "🎸 Schwere, verzerrte Gitarrenriffs",
                "🥁 Wuchtige und präzise Schlagzeug-Patterns",
                "🎻 Einsatz von orchestralen Elementen wie Streichern und Klavier",
                "🎤 Dynamischer Gesang, der zwischen klaren Melodien und Shouts/Screams wechselt",
                "🎹 Integration von elektronischen Klängen und Synthesizern",
                "🎭 Dramatische und emotionale Songstrukturen"
            ]
        },
        "examples": {
            "en": "Artists like Red, Linkin Park, Breaking Benjamin",
            "de": "Künstler wie Red, Linkin Park, Breaking Benjamin"
        }
    },
    "Reggae": {
        "tempo": "60-90 BPM",
        "instrumentation": {
            "en": "guitar skank, bass guitar, drums, organ, percussion",
            "de": "Guitar Skank, Bass Guitar, Drums, Orgel, Percussion"
        },
        "vocals": {
            "en": "reggae vocals, patois influences, conscious lyrics",
            "de": "Reggae-Vocals, Patois-Einflüsse, bewusste Texte"
        },
        "mood": {
            "en": "laid-back, conscious, spiritual",
            "de": "laid-back, bewusst, spirituell"
        },
        "description": {
            "en": "Reggae with characteristic rhythms and conscious lyrics",
            "de": "Reggae mit charakteristischen Rhythmen und bewussten Texten"
        },
        "characteristics": {
            "en": [
                "🎸 Characteristic guitar skank",
                "🎸 Deep, rhythmic reggae bass",
                "🥁 One-drop drum pattern",
                "🎹 Hammond organ for atmosphere",
                "🎤 Reggae vocals with conscious lyrics",
                "🌴 Laid-back, spiritual atmosphere"
            ],
            "de": [
                "🎸 Charakteristische Guitar-Skank",
                "🎸 Tiefer, rhythmischer Reggae-Bass",
                "🥁 One-Drop-Drum-Pattern",
                "🎹 Hammond-Orgel für Atmosphäre",
                "🎤 Reggae-Vocals mit bewussten Texten",
                "🌴 Laid-back, spirituelle Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like Bob Marley, Jimmy Cliff, Damian Marley",
            "de": "Künstler wie Bob Marley, Jimmy Cliff, Damian Marley"
        }
    },
    "Blues": {
        "tempo": "60-120 BPM",
        "instrumentation": {
            "en": "blues guitar, harmonica, piano, bass, drums",
            "de": "Blues Guitar, Harmonika, Piano, Bass, Drums"
        },
        "vocals": {
            "en": "blues vocals, emotional expression, call and response",
            "de": "Blues-Vocals, emotionaler Ausdruck, Call and Response"
        },
        "mood": {
            "en": "melancholic, emotional, authentic",
            "de": "melancholisch, emotional, authentisch"
        },
        "description": {
            "en": "Blues with emotional vocals and authentic instruments",
            "de": "Blues mit emotionalen Vocals und authentischen Instrumenten"
        },
        "characteristics": {
            "en": [
                "🎸 Characteristic blues guitar",
                "🎵 Expressive harmonica",
                "🎹 Blues piano with characteristic runs",
                "🎸 Walking bass lines",
                "🎤 Emotional blues vocals",
                "💙 Melancholic, authentic atmosphere"
            ],
            "de": [
                "🎸 Charakteristische Blues-Gitarre",
                "🎵 Ausdrucksstarke Harmonika",
                "🎹 Blues-Piano mit charakteristischen Läufen",
                "🎸 Walking Bass-Lines",
                "🎤 Emotionale Blues-Vocals",
                "💙 Melancholische, authentische Atmosphäre"
            ]
        },
        "examples": {
            "en": "Artists like B.B. King, Muddy Waters, Gary Clark Jr.",
            "de": "Künstler wie B.B. King, Muddy Waters, Gary Clark Jr."
        }
    },
    "Custom": {
        "tempo": "Variable",
        "instrumentation": {
            "en": "User-defined",
            "de": "Benutzerdefiniert"
        },
        "vocals": {
            "en": "User-defined",
            "de": "Benutzerdefiniert"
        }, 
        "mood": {
            "en": "User-defined",
            "de": "Benutzerdefiniert"
        },
        "description": {
            "en": "Custom style",
            "de": "Benutzerdefinierter Stil"
        },
        "characteristics": {
            "en": [
                "🎨 Fully customizable style direction",
                "🎵 User-defined instrumentation",
                "🎤 Individual vocal treatment",
                "⚡ Personal tempo specifications",
                "🌈 Own mood and atmosphere",
                "🎯 Tailored for special requirements"
            ],
            "de": [
                "🎨 Vollständig anpassbare Stilrichtung",
                "🎵 Benutzerdefinierte Instrumentierung",
                "🎤 Individuelle Vocal-Behandlung",
                "⚡ Persönliche Tempo-Vorgaben",
                "🌈 Eigene Stimmung und Atmosphäre",
                "🎯 Maßgeschneidert für spezielle Anforderungen"
            ]
        },
        "examples": {
            "en": "Define your own unique style",
            "de": "Definiere deinen eigenen einzigartigen Stil"
        }
    }
}

def get_style_description(genre: str, custom_style: str = "") -> str:
    """Generiert Stilbeschreibung basierend auf Genre-Auswahl"""
    lang = st.session_state.get('language', 'en')
    
    if genre == "Custom" and custom_style:
        return custom_style
    elif genre in GENRE_STYLES:
        style_info = GENRE_STYLES[genre]
        instrumentation = style_info['instrumentation'].get(lang, style_info['instrumentation'].get('en', ''))
        vocals = style_info['vocals'].get(lang, style_info['vocals'].get('en', ''))
        mood = style_info['mood'].get(lang, style_info['mood'].get('en', ''))
        return f"Genre: {genre}, Tempo: {style_info['tempo']}, Instrumentation: {instrumentation}, Vocals: {vocals}, Mood: {mood}"
    else:
        if lang == 'de':
            return "Emotionale Ballade mit Piano und Strings"
        else:
            return "Emotional ballad with piano and strings"

def display_genre_info(genre: str):
    """Zeigt detaillierte Genre-Informationen an"""
    lang = st.session_state.get('language', 'en')
    
    if genre in GENRE_STYLES:
        info = GENRE_STYLES[genre]
        
        # Hole sprachspezifische Inhalte
        description = info['description'].get(lang, info['description'].get('en', ''))
        characteristics = info['characteristics'].get(lang, info['characteristics'].get('en', []))
        examples = info['examples'].get(lang, info['examples'].get('en', ''))
        instrumentation = info['instrumentation'].get(lang, info['instrumentation'].get('en', ''))
        vocals = info['vocals'].get(lang, info['vocals'].get('en', ''))
        mood = info['mood'].get(lang, info['mood'].get('en', ''))
        
        # Hauptinfo-Box mit glasmorphism
        st.markdown(f"""
        <div class="genre-info-container">
            <div style="
                background: linear-gradient(135deg, rgba(138, 43, 226, 0.3) 0%, rgba(75, 0, 130, 0.2) 100%);
                padding: 2rem;
                border-radius: 20px;
                margin: 1rem 0;
                color: white;
                box-shadow: 0 8px 32px rgba(138, 43, 226, 0.2);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(138, 43, 226, 0.3);
            ">
                <h3 style="margin: 0 0 1.5rem 0; font-size: 2rem; font-weight: 700; 
                          background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
                          -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                          background-clip: text;">🎵 {genre}</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; margin-bottom: 1.5rem;">
                    <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 12px; backdrop-filter: blur(10px);">
                        <strong style="color: #4ecdc4;">⏱️ Tempo:</strong><br>
                        <span style="font-size: 1.1rem;">{info['tempo']}</span>
                    </div>
                    <div style="background: rgba(255, 255, 255, 0.1); padding: 1rem; border-radius: 12px; backdrop-filter: blur(10px);">
                        <strong style="color: #4ecdc4;">🎭 {'Stimmung' if lang == 'de' else 'Mood'}:</strong><br>
                        <span style="font-size: 1.1rem;">{mood}</span>
                    </div>
                </div>
                <div style="background: rgba(255, 255, 255, 0.1); padding: 1.5rem; border-radius: 12px; backdrop-filter: blur(10px);">
                    <strong style="color: #ff6b6b;">📝 {'Beschreibung' if lang == 'de' else 'Description'}:</strong><br>
                    <span style="font-size: 1.1rem; line-height: 1.6;">{description}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Charakteristika in modernem Card-Layout
        st.markdown(f"### 🎯 {'Genre-Charakteristika' if lang == 'de' else 'Genre Characteristics'}:")
        
        # Erstelle Cards für Charakteristika
        cols = st.columns(2)
        for i, char in enumerate(characteristics):
            with cols[i % 2]:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
                    backdrop-filter: blur(15px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 12px;
                    padding: 1rem;
                    margin: 0.5rem 0;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
                " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 8px 30px rgba(0, 0, 0, 0.2)';"
                   onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 20px rgba(0, 0, 0, 0.1)';">
                    <span style="color: rgba(255, 255, 255, 0.9); font-size: 0.95rem; line-height: 1.5;">• {char}</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Beispiele in einer schönen Box
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(138, 43, 226, 0.1) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1.5rem 0;
            box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        ">
            <strong style="color: #4ecdc4; font-size: 1.1rem;">🎤 {'Beispiele' if lang == 'de' else 'Examples'}:</strong><br>
            <span style="color: rgba(255, 255, 255, 0.9); font-size: 1rem; line-height: 1.6;">{examples}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Instrumentierung Details in separater Card
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(60, 60, 60, 0.6) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            border-left: 4px solid #667eea;
        ">
            <div style="margin-bottom: 1rem;">
                <strong style="color: #667eea; font-size: 1.1rem;">🎼 {'Instrumentierung' if lang == 'de' else 'Instrumentation'}:</strong><br>
                <span style="color: rgba(255, 255, 255, 0.9); line-height: 1.6;">{instrumentation}</span>
            </div>
            <div>
                <strong style="color: #667eea; font-size: 1.1rem;">🎤 Vocals:</strong><br>
                <span style="color: rgba(255, 255, 255, 0.9); line-height: 1.6;">{vocals}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 3) Credits-Anzeige für sunoapi.org
# -------------------------------------------------------------------------
def get_remaining_credits() -> dict:
    """Holt die verbleibenden Credits von sunoapi.org"""
    try:
        headers = {"Authorization": f"Bearer {API_KEY}"}
        response = requests.get(f"{BASE_URL}/api/v1/generate/credit", headers=headers, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        if data.get("code") == 200:
            # Die API gibt direkt die Credits als "data" zurück (integer)
            credits = data.get("data", 0)
            return {
                "success": True,
                "credits": credits,
                "total_credits": None,  # Diese Info ist nicht verfügbar
                "used_credits": None    # Diese Info ist nicht verfügbar
            }
        else:
            return {"success": False, "error": data.get("msg", "Unbekannter Fehler")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def display_credits_info():
    """Zeigt die Credits-Informationen in der Sidebar an"""
    with st.sidebar:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(138, 43, 226, 0.2) 0%, rgba(75, 0, 130, 0.15) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(138, 43, 226, 0.3);
            border-radius: 16px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 8px 32px rgba(138, 43, 226, 0.2);
        ">
            <h3 style="
                color: #4ecdc4; 
                font-size: 1.3rem; 
                font-weight: 600; 
                margin-bottom: 1rem;
                text-align: center;
            ">{get_text("credits_status")}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        credits_info = get_remaining_credits()
        
        if credits_info["success"]:
            credits = credits_info["credits"]
            
            # Credits-Anzeige mit modernem Design
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            ">
                <div style="
                    font-size: 2.5rem; 
                    font-weight: 700; 
                    background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
                    -webkit-background-clip: text; 
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    margin-bottom: 0.5rem;
                ">{credits:,}</div>
                <div style="color: rgba(255, 255, 255, 0.8); font-size: 0.9rem;">{get_text("remaining_credits")}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Farbkodierte Warnung basierend auf verbleibenden Credits
            if credits < 10:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(244, 67, 54, 0.2) 0%, rgba(244, 67, 54, 0.1) 100%);
                    border: 1px solid rgba(244, 67, 54, 0.3);
                    border-radius: 12px;
                    padding: 1rem;
                    margin: 1rem 0;
                    backdrop-filter: blur(10px);
                    text-align: center;
                ">
                    <span style="color: #ff6b6b; font-weight: 600;">{get_text("low_credits_warning")}</span>
                </div>
                """, unsafe_allow_html=True)
            elif credits < 50:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(255, 152, 0, 0.2) 0%, rgba(255, 152, 0, 0.1) 100%);
                    border: 1px solid rgba(255, 152, 0, 0.3);
                    border-radius: 12px;
                    padding: 1rem;
                    margin: 1rem 0;
                    backdrop-filter: blur(10px);
                    text-align: center;
                ">
                    <span style="color: #feca57; font-weight: 600;">{get_text("credits_running_low")}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%);
                    border: 1px solid rgba(76, 175, 80, 0.3);
                    border-radius: 12px;
                    padding: 1rem;
                    margin: 1rem 0;
                    backdrop-filter: blur(10px);
                    text-align: center;
                ">
                    <span style="color: #4ecdc4; font-weight: 600;">{get_text("sufficient_credits")}</span>
                </div>
                """, unsafe_allow_html=True)
                
        else:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(244, 67, 54, 0.2) 0%, rgba(244, 67, 54, 0.1) 100%);
                border: 1px solid rgba(244, 67, 54, 0.3);
                border-radius: 12px;
                padding: 1rem;
                margin: 1rem 0;
                backdrop-filter: blur(10px);
                text-align: center;
            ">
                <span style="color: #ff6b6b; font-weight: 600;">{get_text("credits_fetch_error")}</span><br>
                <span style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">{credits_info['error']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        # Refresh-Button mit modernem Design
        if st.button(get_text("refresh_credits"), use_container_width=True):
            try:
                # Versuche zuerst die neue Funktion
                st.rerun()
            except AttributeError:
                # Fallback für ältere Streamlit-Versionen
                st.experimental_rerun()
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(138, 43, 226, 0.1) 100%);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(102, 126, 234, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            text-align: center;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.1);
        ">
            <span style="color: #4ecdc4; font-weight: 600;">{get_text("api_provider")}</span>
        </div>
        """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 4) Ollama Integration - FIXED VERSION
# -------------------------------------------------------------------------
def clean_lyrics_output(raw_output: str) -> str:
    """
    Bereinigt die Ausgabe von Ollama und entfernt unerwünschte Erklärungen
    """
    # Entferne häufige Einleitungsphrasen
    unwanted_phrases = [
        r"Okay,?\s*hier ist ein.*?:",
        r"Hier ist ein.*?:",
        r"Ich habe.*?erstellt:",
        r"Der folgende.*?:",
        r"Basierend auf.*?:",
        r"Hier sind die.*?:",
        r".*?im\s+\w+\s+Stil.*?:",
        r".*?passend zu.*?:",
        r".*?entsprechend.*?:",
        r".*?Genre.*?:",
        r".*?Songtext.*?:",
        r".*?Lyrics.*?:",
        r".*?Text.*?:",
    ]
    
    cleaned = raw_output.strip()
    
    # Entferne Einleitungsphrasen am Anfang
    for phrase in unwanted_phrases:
        cleaned = re.sub(phrase, "", cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # Entferne leere Zeilen am Anfang
    cleaned = cleaned.lstrip('\n\r ')
    
    # Finde den ersten Song-Abschnitt (Verse, Chorus, etc.)
    song_sections = [r'\[Verse', r'\[Chorus', r'\[Pre-Chorus', r'\[Bridge', r'\[Intro', r'\[Outro']
    
    for section in song_sections:
        match = re.search(section, cleaned, re.IGNORECASE)
        if match:
            # Beginne ab dem ersten gefundenen Song-Abschnitt
            cleaned = cleaned[match.start():]
            break
    
    return cleaned.strip()

def generate_lyrics_with_ollama(song_description: str, genre: str, style_description: str) -> tuple[str, str]:
    """
    Generiert Songtexte mit Ollama basierend auf Genre und Stilbeschreibung
    Returns: (lyrics, style_description)
    """
    genre_context = ""
    if genre != "Custom":
        genre_info = GENRE_STYLES.get(genre, {})
        genre_context = f"""
GENRE-KONTEXT ({genre}):
- Tempo: {genre_info.get('tempo', 'Variable')}
- Typische Stimmung: {genre_info.get('mood', 'Variable')}
- Charakteristika: {genre_info.get('description', 'Variable')}
"""

    prompt = f"""Du bist ein professioneller Songwriter. Schreibe AUSSCHLIESSLICH Songtexte im korrekten Format.

SONG-BESCHREIBUNG: "{song_description}"
{genre_context}
STIL: {style_description}

WICHTIGE REGELN:
- Gib NUR den Songtext aus, KEINE Erklärungen oder Kommentare
- Beginne DIREKT mit [Verse 1] oder [Intro]
- Verwende AUSSCHLIESSLICH diese Struktur:

[Verse 1]
...

[Pre-Chorus]
...

[Chorus]
...

[Verse 2]
...

[Pre-Chorus]
...

[Chorus]
...

[Bridge]
...

[Final Chorus]
...

- Maximal 5000 Zeichen
- Inhalt muss zum Genre "{genre}" passen
- KEINE Einleitungen wie "Hier ist ein Songtext..." oder ähnliches
- STARTE SOFORT mit dem ersten Song-Abschnitt

Generiere jetzt den Songtext:"""

    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "max_tokens": 2000
            }
        }
        
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json=payload,
            timeout=120
        )
        response.raise_for_status()
        
        result = response.json()
        raw_output = result.get("response", "")
        
        # Bereinige die Ausgabe von unerwünschten Erklärungen
        cleaned_lyrics = clean_lyrics_output(raw_output)
        
        # Begrenze auf 5000 Zeichen
        lyrics = cleaned_lyrics[:5000]
        
        return lyrics, style_description
        
    except Exception as e:
        st.error(f"❌ Ollama-Fehler: {e}")
        return "", ""

# -------------------------------------------------------------------------
# 5) Streamlit‑Setup
# -------------------------------------------------------------------------

# Initialize language first
init_language()

st.set_page_config(
    page_title=get_text("app_title"),
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Initialize session state
if 'selected_genre' not in st.session_state:
    st.session_state.selected_genre = "Deep House"

# Language selector in sidebar
with st.sidebar:
    st.markdown("---")
    selected_language = st.selectbox(
        "🌐 Language / Sprache:",
        options=list(LANGUAGES.keys()),
        format_func=lambda x: LANGUAGES[x],
        index=list(LANGUAGES.keys()).index(st.session_state.language),
        key="language_selector"
    )
    
    # Save language to config if changed
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        save_language(selected_language)
        st.rerun()
    
    import streamlit as st
    if not hasattr(st, "rerun"):        # Streamlit ≤1.26
        st.rerun = st.experimental_rerun

# Credits-Anzeige in der Sidebar
display_credits_info()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* Global Styles */
.stApp {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%);
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

.stDeployButton {display: none;}

/* Ensure sidebar collapse button is visible */
button[kind="header"] {
    visibility: visible !important;
    display: block !important;
}

.css-1rs6os.edgvbvh3 {
    visibility: visible !important;
    display: block !important;
}

/* Main container */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1600px; /* Increased width */
}

/* Glassmorphism card base */
.glass-card {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    transition: all 0.3s ease;
}

.glass-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border-color: rgba(138, 43, 226, 0.3);
}

/* Header styling */
.main-header {
    background: linear-gradient(135deg, rgba(138, 43, 226, 0.3) 0%, rgba(75, 0, 130, 0.3) 100%);
    border: 1px solid rgba(138, 43, 226, 0.3);
    border-radius: 24px;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(138, 43, 226, 0.2);
}

.main-header h1 {
    background: linear-gradient(135deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4, #feca57);
    background-size: 300% 300%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradient 3s ease infinite;
    font-size: 3.5rem;
    font-weight: 700;
    margin: 0;
}

@keyframes gradient {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.main-header p {
    color: rgba(255, 255, 255, 0.8);
    font-size: 1.3rem;
    margin: 1rem 0 0 0;
    font-weight: 400;
}

/* Agent description */
.agent-description {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.8) 0%, rgba(45, 45, 45, 0.6) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(138, 43, 226, 0.2);
    border-radius: 20px;
    padding: 2rem;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.agent-description h3 {
    color: #ff6b6b;
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

.agent-description p, .agent-description li {
    color: rgba(255, 255, 255, 0.85);
    line-height: 1.6;
    font-size: 1rem;
}

.agent-description ul {
    padding-left: 1.5rem;
}

.agent-description li {
    margin-bottom: 0.5rem;
}

/* Genre info styling */
.genre-info-container {
    background: linear-gradient(135deg, rgba(75, 0, 130, 0.15) 0%, rgba(138, 43, 226, 0.1) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(138, 43, 226, 0.2);
    border-radius: 20px;
    padding: 2rem;
    margin: 1.5rem 0;
    box-shadow: 0 8px 32px rgba(138, 43, 226, 0.1);
}

.live-style-display {
    background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(60, 60, 60, 0.6) 100%);
    backdrop-filter: blur(20px);
    border: 2px solid rgba(102, 126, 234, 0.3);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
}

.live-style-display h4 {
    color: #4ecdc4;
    font-weight: 600;
    margin-bottom: 1rem;
}

.live-style-display p {
    color: rgba(255, 255, 255, 0.9);
    font-style: italic;
    margin: 0;
    line-height: 1.5;
}

/* Form styling */
.stForm {
    background: linear-gradient(135deg, rgba(30, 30, 30, 0.8) 0%, rgba(45, 45, 45, 0.6) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Input styling */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 2px solid rgba(138, 43, 226, 0.3) !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.75rem !important;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stSelectbox > div > div > select:focus {
    border-color: rgba(138, 43, 226, 0.6) !important;
    box-shadow: 0 0 20px rgba(138, 43, 226, 0.3) !important;
    background: rgba(255, 255, 255, 0.08) !important;
}

/* Button styling */
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    padding: 0.75rem 2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
}

/* Selectbox styling */
.stSelectbox > div > div {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 2px solid rgba(138, 43, 226, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

/* Checkbox styling */
.stCheckbox > label {
    color: rgba(255, 255, 255, 0.9) !important;
    font-family: 'Inter', sans-serif !important;
}

/* Metrics styling */
.metric-container {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 0.5rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

/* Progress bar styling */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    border-radius: 10px !important;
}

.stProgress > div > div > div {
    background: rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
}

/* Sidebar styling */


/* Success/Error/Warning styling */
.stSuccess {
    background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%) !important;
    border: 1px solid rgba(76, 175, 80, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

.stError {
    background: linear-gradient(135deg, rgba(244, 67, 54, 0.2) 0%, rgba(244, 67, 54, 0.1) 100%) !important;
    border: 1px solid rgba(244, 67, 54, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

.stWarning {
    background: linear-gradient(135deg, rgba(255, 152, 0, 0.2) 0%, rgba(255, 152, 0, 0.1) 100%) !important;
    border: 1px solid rgba(255, 152, 0, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

.stInfo {
    background: linear-gradient(135deg, rgba(33, 150, 243, 0.2) 0%, rgba(33, 150, 243, 0.1) 100%) !important;
    border: 1px solid rgba(33, 150, 243, 0.3) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

/* Expander styling */
.streamlit-expanderHeader {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
    backdrop-filter: blur(10px);
}

/* Audio player styling */
.stAudio {
    background: rgba(255, 255, 255, 0.05) !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    backdrop-filter: blur(10px);
}

/* Download button special styling */
.download-button {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%) !important;
    border: none !important;
    border-radius: 12px !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    padding: 1rem 2rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3) !important;
    width: 100% !important;
}

.download-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(255, 107, 107, 0.4) !important;
    background: linear-gradient(135deg, #ee5a24 0%, #ff6b6b 100%) !important;
}

/* Generation status styling */
.generation-status {
    background: linear-gradient(135deg, rgba(45, 45, 45, 0.8) 0%, rgba(60, 60, 60, 0.6) 100%);
    backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

/* Spinner customization */
.stSpinner > div {
    border-top-color: #667eea !important;
}

/* Custom scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* Responsive design */
@media (max-width: 768px) {
    .main-header h1 {
        font-size: 2.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
    }
    
    .glass-card {
        padding: 1.5rem;
        margin: 0.5rem 0;
    }
}

/* Animation for cards */
@keyframes fadeInUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.glass-card {
    animation: fadeInUp 0.6s ease-out;
}

/* Floating particles background effect */
.stApp::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-image: 
        radial-gradient(circle at 20% 80%, rgb(138, 43, 226) 0%, transparent 50%),
        radial-gradient(circle at 80% 20%, rgb(102, 126, 234) 0%, transparent 50%),
        radial-gradient(circle at 40% 40%, rgb(255, 107, 107) 0%, transparent 50%);
    pointer-events: none;
    z-index: -1;
}
</style>""", unsafe_allow_html=True)

# Header
st.markdown(f"""
<div class="main-header">
    <h1>{get_text("app_title")}</h1>
    <p style="font-size: 1.2em; margin: 0;">{get_text("app_subtitle")}</p>
</div>
""", unsafe_allow_html=True)

# Agent Beschreibung
features_list = "\n".join([f"        <li>{feature}</li>" for feature in get_text("features")])
st.markdown(f"""
<div class="agent-description">
    <h3>{get_text("how_it_works")}</h3>
    <p>{get_text("how_it_works_desc")}</p>
    <ul>
{features_list}
    </ul>
    <p><strong>{get_text("new_feature").split(':')[0]}:</strong> {get_text("new_feature")}</p>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 6) UI-Zustandsverwaltung
# -------------------------------------------------------------------------
# Initialisiere UI-Zustand
if 'show_creation_interface' not in st.session_state:
    st.session_state.show_creation_interface = False

# Zeige nur die Erstellungsoberfläche wenn Song erstellt wird
if not st.session_state.show_creation_interface:
    # Zeige die Hauptoberfläche nur wenn nicht in der Erstellungsphase
    # -------------------------------------------------------------------------
    # 7) Genre-Auswahl mit Live-Anzeige
    # -------------------------------------------------------------------------
    st.subheader(get_text("genre_selection"))

    # Genre-Dropdown mit verbesserter Session State Verwaltung
    if 'genre_selector' not in st.session_state:
        st.session_state.genre_selector = st.session_state.selected_genre

    selected_genre = st.selectbox(
        get_text("choose_genre"),
        options=list(GENRE_STYLES.keys()),
        index=list(GENRE_STYLES.keys()).index(st.session_state.selected_genre),
        key="genre_selector",
        help=get_text("choose_genre")
    )

    # Synchronisiere session state nur wenn sich die Auswahl geändert hat
    if selected_genre != st.session_state.selected_genre:
        st.session_state.selected_genre = selected_genre

    # Live-Anzeige der Genre-Informationen
    st.markdown(f"### {get_text('live_style_preview')}")
    display_genre_info(selected_genre)

    # -------------------------------------------------------------------------
    # 8) Eingabeformular
    # -------------------------------------------------------------------------
    with st.form("song_generator_form"):
        st.subheader(get_text("song_config"))
        
        # Zeige aktuell gewähltes Genre
        st.info(f"{get_text('selected_genre')} **{selected_genre}**")
        
        # Instrumental Option
        instrumental = st.checkbox(get_text("instrumental_only"), value=False)
        
        # Custom Style für Custom Genre
        custom_style = ""
        if selected_genre == "Custom":
            custom_style = st.text_area(
                get_text("custom_style_desc"),
                height=100,
                placeholder=get_text("custom_style_placeholder"),
                help=get_text("custom_style_help")
            )
        
        # Song-Beschreibung
        song_description = st.text_area(
            get_text("song_description"),
            height=120,
            placeholder=get_text("song_desc_placeholder"),
            help=get_text("song_desc_help")
        )
        
        # Status-Info
        if selected_genre != "Custom":
            preview_style = get_style_description(selected_genre, custom_style)
            st.markdown(f"""
            <div class="live-style-display">
                <h4>{get_text("generated_style")}</h4>
                <p style="font-style: italic; margin: 0;">{preview_style}</p>
            </div>
            """, unsafe_allow_html=True)
        
        submitted = st.form_submit_button(get_text("create_song"), use_container_width=True)
        
        # Wenn Submit geklickt wird, wechsle zur Erstellungsoberfläche
        if submitted:
            # Speichere die Eingaben im Session State
            st.session_state.creation_data = {
                'selected_genre': selected_genre,
                'instrumental': instrumental,
                'custom_style': custom_style,
                'song_description': song_description
            }
            st.session_state.show_creation_interface = True
            st.rerun()

else:
    # -------------------------------------------------------------------------
    # 9) Song-Erstellungsoberfläche
    # -------------------------------------------------------------------------
    # Verstecke die Hauptoberfläche vollständig während der Songerstellung
    st.markdown("""
    <style>
    /* Verstecke die Hauptoberfläche vollständig während der Songerstellung */
    .main-header,
    .agent-description {
        display: none !important;
    }
    
    /* Vollbildmodus für die Erstellungsoberfläche */
    .main .block-container {
        padding-top: 1rem;
        max-width: 100%;
    }
    
    /* Spezielle Styling für die Erstellungsoberfläche */
    .creation-interface {
        background: linear-gradient(135deg, rgba(10, 10, 10, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%);
        min-height: 100vh;
        padding: 2rem;
        border-radius: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container für die Erstellungsoberfläche
    st.markdown('<div class="creation-interface">', unsafe_allow_html=True)
    
    # Hole die gespeicherten Daten
    creation_data = st.session_state.get('creation_data', {})
    selected_genre = creation_data.get('selected_genre', 'Deep House')
    instrumental = creation_data.get('instrumental', False)
    custom_style = creation_data.get('custom_style', '')
    song_description = creation_data.get('song_description', '')
    
    # Zeige einen "Zurück" Button
    if st.button("← Zurück zu den Einstellungen", key="back_button"):
        st.session_state.show_creation_interface = False
        st.rerun()
    
    st.markdown("---")
    
    # Zeige die aktuellen Einstellungen als Info
    st.info(f"🎵 **Genre:** {selected_genre} | 🎤 **Instrumental:** {'Ja' if instrumental else 'Nein'}")
    
    # Setze submitted auf True für die nachfolgende Logik
    submitted = True

# -------------------------------------------------------------------------
# 8) API‑Hilfsfunktionen (unverändert)
# -------------------------------------------------------------------------
def post_api_request(path: str, payload: dict) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{BASE_URL}{path}", json=payload, headers=headers, timeout=45)
        r.raise_for_status()
        res = r.json()
        if isinstance(res, dict) and res.get("code") not in (200, 201, None):
            raise RuntimeError(res.get("msg", "Unbekannter API‑Fehler"))
        return res
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"API‑/Netzwerkfehler: {e}")

def extract_task_id(resp: dict) -> str | None:
    candidates = ("taskId", "task_id", "id", "task_uuid")
    data = resp.get("data", {})
    if isinstance(data, dict):
        for k in candidates:
            if data.get(k):
                return str(data[k])
    if isinstance(data, list) and data and isinstance(data[0], dict):
        for k in candidates:
            if data[0].get(k):
                return str(data[0][k])
    for k in candidates:
        if resp.get(k):
            return str(resp[k])
    return None

def get_task_info(task_id: str) -> dict:
    headers = {"Authorization": f"Bearer {API_KEY}"}
    params  = {"taskId": task_id.strip()}
    r = requests.get(f"{BASE_URL}/api/v1/generate/record-info",
                     headers=headers, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def is_generation_complete(info: dict) -> tuple[bool, bool, list]:
    data   = info.get("data", {})
    status = (data.get("status") or "").upper()

    if status.endswith("FAILED") or status in ("EXPIRED",
            "CREATE_TASK_FAILED", "GENERATE_AUDIO_FAILED"):
        return True, True, []

    if status != "SUCCESS":
        return False, False, []

    tracks = data.get("response", {}).get("sunoData", [])
    return True, False, tracks

def download_audio(url: str) -> bytes:
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content

# -------------------------------------------------------------------------
# 9) Hauptlogik
# -------------------------------------------------------------------------
if submitted:
    if not song_description.strip():
        st.error(get_text("song_desc_required"))
        st.stop()
    
    if selected_genre == "Custom" and not custom_style.strip():
        st.error(get_text("custom_style_required"))
        st.stop()

    # Generiere Stilbeschreibung basierend auf Genre
    style_description = get_style_description(selected_genre, custom_style)

    # Phase 1: Lyrics generieren mit verbesserter visueller Anzeige
    st.markdown('<div class="generation-status">', unsafe_allow_html=True)
    st.subheader(get_text("generating_lyrics", genre=selected_genre))
    
    # Erstelle Container für Lyrics-Generierung
    lyrics_progress_container = st.empty()
    
    # Zeige Fortschritt für Lyrics-Generierung
    with lyrics_progress_container.container():
        show_enhanced_progress(
            phase="🧠 KI analysiert Ihre Beschreibung...",
            progress=25,
            genre=selected_genre,
            additional_info="Ollama AI verarbeitet Ihre Eingaben..."
        )
    
    # Simuliere Fortschritt während der Lyrics-Generierung
    time.sleep(1)
    with lyrics_progress_container.container():
        show_enhanced_progress(
            phase="📝 Songtexte werden generiert...",
            progress=75,
            genre=selected_genre,
            additional_info="Kreative Texte werden erstellt..."
        )
    
    # Generiere tatsächlich die Lyrics
    lyrics, final_style = generate_lyrics_with_ollama(song_description, selected_genre, style_description)
    
    # Zeige Fertigstellung der Lyrics-Generierung
    with lyrics_progress_container.container():
        if lyrics:
            show_enhanced_progress(
                phase="✅ Songtexte erfolgreich generiert!",
                progress=100,
                genre=selected_genre,
                additional_info="Lyrics sind bereit für die Musikproduktion!"
            )
        else:
            st.error(get_text("lyrics_error"))
            st.stop()
    
    time.sleep(2)  # Kurze Pause für visuelle Wirkung
    
    # Zeige generierte Inhalte
    with st.expander(get_text("show_lyrics")):
        st.text_area(get_text("lyrics_label"), lyrics, height=200, disabled=True)
        st.text_input(get_text("style_label"), final_style, disabled=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Phase 2: Song erstellen
    st.markdown('<div class="generation-status">', unsafe_allow_html=True)
    st.subheader(get_text("creating_song", genre=selected_genre))
    
    # Payload für Suno API (immer V4_5 und Custom Mode)
    payload = {
        "model": "V4_5",
        "customMode": True,
        "instrumental": instrumental,
        "style": final_style[:1000],
        "prompt": lyrics[:5000],
        "title": textwrap.shorten(f"{selected_genre}: {song_description}", width=80, placeholder="…") or f"AI-Generated {selected_genre} Song",
        "callBackUrl": "https://webhook.site/placeholder"
    }

    st.info(get_text("song_order_received", genre=selected_genre))
    
    try:
        initial = post_api_request("/api/v1/generate", payload)
        st.success(get_text("song_generation_started"))
    except RuntimeError as e:
        st.error(get_text("api_error", error=e))
        st.stop()

    task_id = extract_task_id(initial)
    if not task_id:
        st.error(get_text("task_id_error"))
        st.stop()

    # Verbesserte visuelle Anzeige während der Song-Erstellung
    progress_container = st.empty()
    start = time.time()
    errors = 0
    audio_url = None
    tracks = []

    # Definiere die Phasen für die visuelle Anzeige
    phases = [
        {"name": "🚀 Song-Auftrag wird verarbeitet...", "duration": 30},
        {"name": "🎵 Musikkomposition wird erstellt...", "duration": 60},
        {"name": "🎤 Vocals werden hinzugefügt...", "duration": 90},
        {"name": "✨ Finalisierung und Mastering...", "duration": 120}
    ]
    
    current_phase_index = 0
    
    while True:
        if time.time() - start > TIMEOUT_HARD:
            st.error(get_text("timeout_error"))
            st.stop()

        time.sleep(POLL_DELAY)

        try:
            info = get_task_info(task_id)
            finished, failed, tracks = is_generation_complete(info)
            errors = 0
        except RuntimeError as e:
            errors += 1
            if errors >= 5:
                st.error(get_text("connection_errors"))
                st.stop()
            continue

        if failed:
            st.error(get_text("generation_failed"))
            st.stop()

        if finished:
            if tracks:
                audio_url = tracks[0].get("audioUrl") or tracks[0].get("audio_url")
            break

        # Berechne Fortschritt und aktuelle Phase
        elapsed = time.time() - start
        total_progress = min(int(elapsed / 240 * 100), 95)
        
        # Bestimme aktuelle Phase basierend auf verstrichener Zeit
        for i, phase in enumerate(phases):
            if elapsed <= phase["duration"]:
                current_phase_index = i
                break
        else:
            current_phase_index = len(phases) - 1
        
        current_phase = phases[current_phase_index]["name"]
        
        # Zusätzliche Informationen basierend auf API-Status
        status_txt = (info.get("data", {}).get("status") or "...").upper()
        additional_info = f"API Status: {status_txt} | Verstrichene Zeit: {int(elapsed)}s"
        
        # Zeige verbesserte Fortschrittsanzeige
        with progress_container.container():
            show_enhanced_progress(
                phase=current_phase,
                progress=total_progress,
                genre=selected_genre,
                additional_info=additional_info
            )

    # Zeige Fertigstellungs-Animation
    with progress_container.container():
        show_enhanced_progress(
            phase="🎉 Song erfolgreich erstellt!",
            progress=100,
            genre=selected_genre,
            additional_info="Ihr Song ist bereit zum Download!"
        )
        st.markdown(create_completion_celebration(selected_genre), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Ergebnis anzeigen
    if not audio_url:
        st.error(get_text("no_audio_error"))
        st.stop()

    st.success(get_text("song_ready", genre=selected_genre))
    
    track_info = tracks[0] if tracks else {}
    
    # Song Info
    col1, col2 = st.columns(2)
    with col1:
        st.metric(get_text("title_metric"), track_info.get('title', 'N/A'))
        st.metric(get_text("genre_metric"), selected_genre)
    with col2:
        st.metric(get_text("duration_metric"), f"{track_info.get('duration', 'N/A')} s")
        st.metric(get_text("model_metric"), track_info.get('model_name', 'V4_5'))

    # Audio Player
    st.audio(audio_url, format="audio/mp3")

    # Download
    try:
        with st.spinner(get_text("preparing_download")):
            mp3_data = download_audio(audio_url)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        mp3_filename = f"ai_{selected_genre.lower().replace(' ', '_')}_{timestamp}.mp3"
        lyrics_filename = f"ai_{selected_genre.lower().replace(' ', '_')}_{timestamp}_lyrics.txt"
        
        # Erstelle Lyrics-Textdatei mit Metadaten
        lyrics_content = f"""Song Title: {track_info.get('title', 'AI Generated Song')}
Genre: {selected_genre}
Style: {final_style}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Duration: {track_info.get('duration', 'N/A')} seconds
Model: {track_info.get('model_name', 'V4_5')}

--- LYRICS ---

{lyrics}

--- END ---

Generated by AI Song Agent
"""
        
        # Speichere Lyrics und Song-Daten in Session State für Persistenz
        if 'current_song_data' not in st.session_state:
            st.session_state.current_song_data = {}
        
        st.session_state.current_song_data = {
            'mp3_data': mp3_data,
            'mp3_filename': mp3_filename,
            'lyrics_content': lyrics_content,
            'lyrics_filename': lyrics_filename,
            'track_info': track_info,
            'genre': selected_genre,
            'audio_url': audio_url,
            'timestamp': timestamp
        }
        
        # Kombinierter Download-Button für Song + Lyrics
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Hauptdownload-Button für Song (automatisch mit Lyrics)
            st.download_button(
                get_text("download_song_with_lyrics", genre=selected_genre),
                mp3_data,
                mp3_filename,
                "audio/mpeg",
                use_container_width=True,
                help=get_text("download_tip")
            )
        
        with col2:
            # Separater Lyrics-Download für Benutzer, die nur die Texte wollen
            st.download_button(
                get_text("download_only_lyrics"),
                lyrics_content.encode('utf-8'),
                lyrics_filename,
                "text/plain",
                use_container_width=True,
                help="Lädt nur die Songtexte als TXT-Datei herunter"
            )
        
        # Automatische Anzeige beider Download-Buttons nach Song-Erstellung
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, rgba(76, 175, 80, 0.2) 0%, rgba(76, 175, 80, 0.1) 100%);
            border: 1px solid rgba(76, 175, 80, 0.3);
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            text-align: center;
        ">
            <span style="color: #4ecdc4; font-weight: 600;">{get_text("download_tip")}</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Zusätzliche Download-Buttons für beide Dateien gleichzeitig
        st.markdown(f"### {get_text('download_all_files')}")
        
        col_mp3, col_txt = st.columns(2)
        with col_mp3:
            st.download_button(
                f"🎵 {mp3_filename}",
                mp3_data,
                mp3_filename,
                "audio/mpeg",
                use_container_width=True
            )
        
        with col_txt:
            st.download_button(
                f"📄 {lyrics_filename}",
                lyrics_content.encode('utf-8'),
                lyrics_filename,
                "text/plain",
                use_container_width=True
            )
        
        st.success(get_text("song_created_success", genre=selected_genre))
        
        # Button zum Zurücksetzen der Oberfläche
        st.markdown("---")
        if st.button("🔄 Neuen Song erstellen", key="new_song_button", use_container_width=True):
            st.session_state.show_creation_interface = False
            if 'creation_data' in st.session_state:
                del st.session_state.creation_data
            st.rerun()
        
    except RuntimeError as e:
        st.error(get_text("download_error", error=e))
        st.info(get_text("direct_link", url=audio_url))
    
    # Schließe den Container für die Erstellungsoberfläche
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 10) Vorherige Downloads Sektion
# -------------------------------------------------------------------------
if 'current_song_data' in st.session_state and st.session_state.current_song_data:
    st.markdown("---")
    lang = st.session_state.get('language', 'en')
    
    if lang == 'de':
        st.subheader("🔄 Vorherige Downloads")
        st.info("Hier können Sie Ihren zuletzt generierten Song und die Songtexte erneut herunterladen:")
    else:
        st.subheader("🔄 Previous Downloads")
        st.info("Here you can re-download your last generated song and lyrics:")
    
    song_data = st.session_state.current_song_data
    
    # Zeige Song-Info
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🎵 Genre", song_data.get('genre', 'N/A'))
        created_label = "📅 Erstellt" if lang == 'de' else "📅 Created"
        st.metric(created_label, song_data.get('timestamp', 'N/A'))
    with col2:
        track_info = song_data.get('track_info', {})
        duration_label = "⏱️ Dauer" if lang == 'de' else "⏱️ Duration"
        st.metric(duration_label, f"{track_info.get('duration', 'N/A')} s")
        st.metric("🤖 Model", track_info.get('model_name', 'V4_5'))
    
    # Audio Player für vorherigen Song
    if song_data.get('audio_url'):
        st.audio(song_data['audio_url'], format="audio/mp3")
    
    # Download-Buttons für vorherigen Song
    col1, col2 = st.columns(2)
    with col1:
        if song_data.get('mp3_data') and song_data.get('mp3_filename'):
            download_help = "Laden Sie Ihren Song erneut herunter" if lang == 'de' else "Re-download your song"
            st.download_button(
                f"🎵 {song_data['mp3_filename']}",
                song_data['mp3_data'],
                song_data['mp3_filename'],
                "audio/mpeg",
                use_container_width=True,
                help=download_help
            )
    
    with col2:
        if song_data.get('lyrics_content') and song_data.get('lyrics_filename'):
            lyrics_help = "Laden Sie die Songtexte erneut herunter" if lang == 'de' else "Re-download the lyrics"
            st.download_button(
                f"📄 {song_data['lyrics_filename']}",
                song_data['lyrics_content'].encode('utf-8'),
                song_data['lyrics_filename'],
                "text/plain",
                use_container_width=True,
                help=lyrics_help
            )
    
    # Button zum Löschen der gespeicherten Daten
    clear_button_text = "🗑️ Gespeicherte Song-Daten löschen" if lang == 'de' else "🗑️ Clear stored song data"
    clear_help = "Löscht die gespeicherten Song-Daten aus dem Speicher" if lang == 'de' else "Clears the stored song data from memory"
    
    if st.button(clear_button_text, help=clear_help):
        del st.session_state.current_song_data
        st.rerun()
