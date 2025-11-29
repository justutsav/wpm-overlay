# WPM Overlay

A simple and lightweight WPM (Words Per Minute) overlay built with Python, Tkinter, and pynput.
Tracks your typing speed in real-time, shows 15s / 30s / 60s WPM, and displays a small graph of your recent performance.
The overlay floats above all windows and can be dragged anywhere on your screen.

# 🚀 Features

📌 Global keystroke tracking (works in all apps)

⏱ Accurate WPM calculation

📊 Live mini graph of past WPM

🎨 Color changes based on your speed

🪟 Draggable floating overlay

🔧 Single-file program — easy to run

🗝 Optional: raw key logging (for debugging)

# 📦 Installation

Install Python dependencies:
```bash
pip install pynput
```

Tkinter comes preinstalled on Windows/macOS.
On Linux, install:
```bash
sudo apt install python3-tk
```
# ▶️ How to Run

Run the overlay:
```bash
python wpm_overlay.py
```

The overlay will appear on your screen and start tracking instantly.

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
├── wpm_overlay.py     # main application (single-file overlay)
└── README.md          # documentation
```

# 📝 License

MIT License — free to use, modify, and share.