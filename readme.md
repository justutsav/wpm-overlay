# WPM Overlay

A simple and lightweight WPM (Words Per Minute) overlay built with Python, Tkinter, and pynput.
Tracks your typing speed in real-time, shows 15s / 30s / 60s WPM, and displays a small graph of your recent performance.
The overlay floats above all windows and can be dragged anywhere on your screen.

# 📸 Screenshots
<p align="center"> <img src="https://raw.githubusercontent.com/justutsav/wpm-overlay/master/Screenshots/Slow.png" width="420" alt="Slow WPM screenshot"/> <br><em>Slow WPM</em> </p> <p align="center"> <img src="https://raw.githubusercontent.com/justutsav/wpm-overlay/master/Screenshots/Medium.png" width="420" alt="Medium WPM screenshot"/> <br><em>Medium WPM</em> </p> <p align="center"> <img src="https://raw.githubusercontent.com/justutsav/wpm-overlay/master/Screenshots/Fast.png" width="420" alt="Fast WPM screenshot"/> <br><em>Fast WPM</em> </p> <p align="center"> <img src="https://raw.githubusercontent.com/justutsav/wpm-overlay/master/Screenshots/Lightning%20mcqueen.png" width="420" alt="Lightning McQueen WPM screenshot"/> <br><em>This is you ig⚡</em> </p>

# 📥 Download
**[Download the latest version here](https://github.com/justutsav/wpm-overlay/releases)**

Just download the `WPM Overlay.exe` and run it. No installation required!

# 🚀 Features

📌 Global keystroke tracking (works in all apps)

⏱ Accurate WPM calculation

📊 Live mini graph of past WPM

🎨 Color changes based on your speed

🪟 Draggable floating overlay

🔧 Single-file program — easy to run

🗝 Optional: raw key logging (for debugging)

# 🛠️ Development / Run from Source

If you want to run the Python script directly or modify the code:

### 1. Install Dependencies
```bash
pip install pynput
# Tkinter is usually pre-installed on Windows/macOS.
# On Linux: sudo apt install python3-tk
```

### 2. Run the Script
```bash
python wpm_overlay.py
```

# 📦 Build it Yourself
To create the executable (`.exe`) from source, we use PyInstaller.

1.  Install PyInstaller:
    ```bash
    pip install pyinstaller
    ```
2.  Run the build command (uses the included `.spec` file):
    ```bash
    pyinstaller "WPM Overlay.spec"
    ```
3.  The executable will appear in the `dist/` folder.

# 🎛 Basic Controls

Drag anywhere on the overlay to move it

Click the × button to close it

Colors change depending on your WPM

Red = slow

Orange = average

Green = good

Blue = excellent

# ⚙️ Optional Settings
Enable word-counting mode

Counts full words instead of individual keystrokes:
```bash
# Windows
set WPM_WORDS=1

# macOS / Linux
export WPM_WORDS=1
```

Enable debug key logging

Creates a keys.log file to help diagnose missed keys:
```bash
set WPM_LOG_KEYS=1
```

# 📁 Files
```bash
wpm-overlay/
│
├── assets/            # Icons and images
├── dist/              # Compiled executable (after build)
├── wpm_overlay.py     # Main application source code
├── WPM Overlay.spec   # PyInstaller build configuration
└── README.md          # Documentation
```

# 📝 License

MIT License — free to use, modify, and share.
