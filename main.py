import subprocess
import os

def main():
    script_path = os.path.join(os.path.dirname(__file__), "song_agent.py")
    # Use 'python' instead of 'python3' for better compatibility on Windows systems.
    # If you still encounter 'Python not found' errors, ensure Python is installed
    # and added to your system's PATH, or try 'py -m streamlit run' if 'py' launcher is available.
    subprocess.run(["python", "-m", "streamlit", "run", script_path])

if __name__ == "__main__":
    main()


