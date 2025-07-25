🤖 AI Song Agent

Your personal AI assistant for song production

🎵 Overview

The AI Song Agent is an intelligent application that automatically generates complete songs based on your descriptions. It combines the power of Ollama for lyrics generation with the Suno API for music creation.

✨ Features

•
📝 Professional Lyrics Generation: Creates lyrics in the correct format using AI

•
🎼 Automatic Style Generation: Generates matching style and mood descriptions based on genre

•
🎧 Complete MP3 Creation: Produces full songs ready for download

•
🌐 Multi-language Support: Available in English and German

•
🎯 Live Style Preview: Interactive genre selection with real-time style information

•
🎨 Multiple Genres: Support for 20+ music genres including:

•
Deep House, Synthpop, Trap, Techno

•
Ambient, Drum & Bass, Future Bass

•
Lo-Fi Hip Hop, Psytrance, Indie Pop

•
And many more...



🚀 How It Works

1.
Choose a Genre: Select from 20+ predefined genres or create a custom style

2.
Describe Your Song: Provide a description of the theme, mood, or story

3.
AI Generation: The system automatically:

•
Generates professional lyrics using Ollama

•
Creates appropriate style descriptions

•
Produces a complete MP3 file via Suno API



4.
Download: Get your finished song as an MP3 file

🛠️ Installation & Setup

Prerequisites

•
Python 3.11+

•
Streamlit

•
Ollama (running locally on port 11434)

•
Suno API key

Installation

1.
Clone or extract the project files

2.
Install dependencies:

3.
Set up your Suno API key:

•
Create .streamlit/secrets.toml

•
Add your API key:



4.
Ensure Ollama is running with the required model:

Running the Application

Bash


streamlit run song_agent.py


Or use the provided start script:

Bash


./start.sh


🎼 Supported Genres

The application supports 20+ music genres with detailed style information:

•
Electronic: Deep House, Synthpop, Trap, Techno, Ambient, Drum & Bass, Future Bass, Psytrance, Hardstyle

•
Hip Hop: Lo-Fi Hip Hop, Reggaeton

•
Pop/Rock: Indie Pop, Pop Rock, Alternative Rock

•
Traditional: Jazz, Classical, R&B, Soul, Country, Folk, Blues

•
Emotional: Piano Ballad, Emotional, Romantic, Acoustic

•
Custom: Define your own style

Each genre includes:

•
Tempo specifications

•
Instrumentation details

•
Vocal characteristics

•
Mood descriptions

•
Example artists

🌐 Language Support

The application supports multiple languages:

•
English (default)

•
German

Language can be switched using the selector in the sidebar.

📁 Project Structure

Plain Text


├── song_agent.py          # Main application file
├── requirements.txt       # Python dependencies
├── start.sh              # Start script
├── README.md             # This file
├── CHANGELOG.md          # Version history
└── .streamlit/
    ├── config.toml       # Streamlit configuration
    └── secrets.toml      # API keys (create this)


🔧 Configuration

Ollama Settings

•
URL: http://localhost:11434

•
Model: gemma3n:e4b

•
Timeout: 120 seconds

Suno API Settings

•
Base URL: https://api.sunoapi.org

•
Model: V4_5 (Custom Mode)

•
Timeout: 600 seconds (10 minutes)

💡 Usage Tips

1.
Genre Selection: Choose a genre that matches your desired style for best results

2.
Song Description: Be specific about mood, theme, and story elements

3.
Custom Styles: When using "Custom" genre, provide detailed style descriptions

4.
Language: Switch language in the sidebar for localized interface

🎨 Features in Detail

Live Style Preview

•
Real-time display of genre characteristics

•
Detailed instrumentation information

•
Tempo and mood specifications

•
Example artists for reference

Credits Management

•
Real-time credits display

•
Color-coded warnings for low credits

•
Direct integration with sunoapi.org

Professional Output

•
High-quality MP3 files

•
Proper song structure (Verse, Chorus, Bridge, etc.)

•
Genre-appropriate styling

•
Downloadable results

🔍 Troubleshooting

Common Issues

1.
API Key Error: Ensure your Suno API key is correctly set in .streamlit/secrets.toml

2.
Ollama Connection: Verify Ollama is running on localhost:11434

3.
Model Not Found: Install the required model: ollama pull gemma3n:e4b

4.
Generation Timeout: Large requests may take up to 10 minutes

Error Messages

The application provides clear error messages in your selected language for:

•
Missing API keys

•
Connection issues

•
Generation failures

•
Insufficient credits

📊 Credits System

The application uses the sunoapi.org credits system:

•
Credits are consumed per song generation

•
Real-time credit balance display

•
Automatic warnings for low credits

•
Refresh functionality

🎵 Output Quality

Generated songs feature:

•
Professional lyrics structure

•
Genre-appropriate instrumentation

•
High-quality audio (MP3 format)

•
Proper song length and arrangement

•
Downloadable files with timestamps

🤝 Contributing

This is a complete, ready-to-use application. For modifications:

1.
Ensure all dependencies are installed

2.
Test changes locally before deployment

3.
Maintain the translation system for multi-language support

📄 License

This project is provided as-is for personal and educational use.

🔗 API Credits

•
Suno API: Powered by sunoapi.org

•
Ollama: Local AI model for lyrics generation

•
Streamlit: Web application framework





Enjoy creating music with AI! 🎵
