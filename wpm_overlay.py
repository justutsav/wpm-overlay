"""
wpm_overlay.py

Overlay WPM tracker using tkinter + pynput.

Features:
- Counts printable characters and spaces (so words are not undercounted).
- Optional WORD mode (counts completed words on space/enter).
- Thread-safe (uses threading.Lock for shared data).
- Uses time.perf_counter() (monotonic) for timing.
- Small graph of recent WPM history.
- Drag anywhere on the overlay (frame, canvas, button).
- Proper cleanup: listener.stop() on close and WM_DELETE_WINDOW handler.
- Optional debug logging to keys.log for diagnosis.

Requirements:
    pip install pynput
"""

import tkinter as tk
from pynput import keyboard
import time
from collections import deque
import threading
import sys
import os

# ---------- Configuration ----------
SAMPLE_INTERVAL_MS = 100        # UI update interval in ms (100 for smooth)
HISTORY_LEN = 60               # how many samples to keep for graph (roughly seconds)
LOG_KEYS = False               # if True, write raw captured events to keys.log
COUNT_WORDS_MODE = False       # False => count keystrokes (including spaces)
                               # True  => count completed words (increment on space/enter)
# Color thresholds (you can tweak these)
COLOR_THRESHOLDS = {
    "slow": (30, "#ff4d4f"),   # <=30 red
    "avg":  (60, "#ffb020"),   # <=60 orange
    "good": (90, "#00c853"),   # <=90 green
    "best": (9999, "#00bcd4")  # >90 cyan
}
# -----------------------------------

class WPMTracker:
    def __init__(self):
        # Tk root
        self.root = tk.Tk()
        self.root.title("WPM Tracker")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.geometry("300x150+100+100")
        self.bg_color = '#1e1e1e'
        self.fg_color = '#00ff00'  # initial accent color
        self.root.configure(bg=self.bg_color)
        self.root.attributes('-alpha', 0.90)  # semi-opaque

        # Close button
        self.close_button = tk.Button(
            self.root,
            text="✕",
            command=self.close,
            bg="#333333",
            fg="#ffffff",
            font=("Consolas", 12, "bold"),
            bd=0,
            activebackground="#ff4444",
            activeforeground="#ffffff"
        )
        self.close_button.place(relx=1.0, x=-10, y=10, anchor="ne")
        self.root.after(100, lambda: self.close_button.lift())

        # State & concurrency
        self.lock = threading.Lock()
        # timestamps_deque stores timestamps for keystrokes mode
        # or timestamps for word completions in words mode
        self.timestamps = deque()
        # In word-mode we accumulate characters in current_word (reset on space/enter)
        self.current_word_chars = []  # protected by lock
        # WPM history (samples per UI tick)
        self.wpm_history = deque(maxlen=HISTORY_LEN)

        # UI
        self.frame = tk.Frame(self.root, bg=self.bg_color)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.label_15s = tk.Label(self.frame, text="15s: 0 WPM", font=("Consolas", 10), fg=self.fg_color, bg=self.bg_color)
        self.label_15s.pack(anchor='w')
        self.label_30s = tk.Label(self.frame, text="30s: 0 WPM", font=("Consolas", 10), fg=self.fg_color, bg=self.bg_color)
        self.label_30s.pack(anchor='w')
        self.label_60s = tk.Label(self.frame, text="60s: 0 WPM", font=("Consolas", 10), fg=self.fg_color, bg=self.bg_color)
        self.label_60s.pack(anchor='w')

        self.canvas_height = 60
        self.canvas = tk.Canvas(self.frame, height=self.canvas_height, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(fill=tk.X, pady=5)

        # Bind dragging to multiple widgets so dragging works from any area
        for widget in (self.root, self.frame, self.canvas, self.close_button):
            widget.bind('<Button-1>', self.start_move)
            widget.bind('<B1-Motion>', self.do_move)

        # Keyboard listener (daemon thread)
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.daemon = True
        self.listener.start()

        # Close handler
        self.root.protocol("WM_DELETE_WINDOW", self.close)

        # Debug / logging file
        self.logfile = os.path.join(os.getcwd(), "keys.log") if LOG_KEYS else None
        if self.logfile and os.path.exists(self.logfile):
            try:
                os.remove(self.logfile)
            except Exception:
                pass

        # Start UI update loop
        self.update_ui()

    # ---------- Dragging ----------
    def start_move(self, event):
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def do_move(self, event):
        try:
            x = event.x_root - self._drag_x
            y = event.y_root - self._drag_y
            self.root.geometry(f"+{x}+{y}")
        except Exception:
            pass

    # ---------- Key press handling ----------
    def on_press(self, key):
        """
        Count a press if:
         - key.char exists and is printable OR
         - key is space or enter (count as keystroke or word separator)
        Ignore pure modifiers (shift/ctrl/alt), function keys, arrows, etc.
        """
        try:
            now = time.perf_counter()
            ch = getattr(key, 'char', None)

            should_count_keystroke = False
            completed_word = False

            if ch is not None:
                # ch is an actual character (could be ' ' in some environments)
                if ch.isprintable():
                    should_count_keystroke = True
                    # If word-mode, add char to buffer
                    if COUNT_WORDS_MODE:
                        with self.lock:
                            self.current_word_chars.append(ch)
                else:
                    # Non-printable char reported as char (rare)
                    pass
            else:
                # ch is None: handle known printable special keys
                if key == keyboard.Key.space:
                    # space counts as keystroke and also completes a word in word-mode
                    should_count_keystroke = True
                    if COUNT_WORDS_MODE:
                        with self.lock:
                            if len(self.current_word_chars) > 0:
                                # commit a word (timestamp)
                                self.timestamps.append(now)
                                self.current_word_chars = []
                elif key == keyboard.Key.enter:
                    # treat Enter as both keystroke and word completion
                    should_count_keystroke = True
                    if COUNT_WORDS_MODE:
                        with self.lock:
                            if len(self.current_word_chars) > 0:
                                self.timestamps.append(now)
                                self.current_word_chars = []
                else:
                    # ignore other special keys (shift, ctrl, alt, arrows, etc.)
                    should_count_keystroke = False

            # Append timestamp for keystrokes mode
            if not COUNT_WORDS_MODE:
                if should_count_keystroke:
                    with self.lock:
                        self.timestamps.append(now)

            # Optional logging for diagnosis
            if LOG_KEYS and self.logfile:
                try:
                    with open(self.logfile, "a", encoding="utf-8") as f:
                        f.write(f"{now:.6f}\tch={repr(ch)}\tkey={repr(str(key))}\n")
                except Exception:
                    pass

        except Exception:
            # Do not raise from listener thread
            return

    # ---------- WPM calculation ----------
    def calculate_count(self, time_window):
        """Return the count of events in the last time_window seconds."""
        now = time.perf_counter()
        cutoff = now - max(70, time_window + 5)
        with self.lock:
            # prune older than cutoff
            while self.timestamps and self.timestamps[0] < cutoff:
                self.timestamps.popleft()
            cnt = sum(1 for t in self.timestamps if t >= now - time_window)
        return cnt

    def calculate_wpm(self, time_window):
        """Standard conversion: 5 keystrokes = 1 word"""
        count = self.calculate_count(time_window)
        words = count / 5.0
        minutes = time_window / 60.0
        wpm = int(words / minutes) if minutes > 0 else 0
        return wpm

    # ---------- Color helper ----------
    def get_color_for_wpm(self, wpm):
        """Return a hex color based on WPM thresholds (editable in COLOR_THRESHOLDS)."""
        for name, (thr, col) in COLOR_THRESHOLDS.items():
            if wpm <= thr:
                return col
        return COLOR_THRESHOLDS["best"][1]

    # ---------- Graph drawing ----------
    def draw_graph(self):
        self.canvas.delete("all")
        if not self.wpm_history:
            return

        width = max(1, self.canvas.winfo_width())
        height = self.canvas_height
        max_wpm = max(self.wpm_history) if self.wpm_history else 10
        max_wpm = max(10, max_wpm)

        num_points = len(self.wpm_history)
        pad_x = 6
        usable_w = max(1, width - 2 * pad_x)

        points = []
        for i, w in enumerate(self.wpm_history):
            if num_points == 1:
                rx = 0.5
            else:
                rx = i / (num_points - 1)
            x = pad_x + rx * usable_w
            y = height - ((w / max_wpm) * height)
            # clamp y
            y = max(1, min(height - 1, y))
            points.extend((x, y))

        if len(points) >= 4:
            # graph uses current accent color
            self.canvas.create_line(points, fill=self.fg_color, width=2, smooth=True)

    # ---------- UI update loop ----------
    def update_ui(self):
        w15 = self.calculate_wpm(15)
        w30 = self.calculate_wpm(30)
        w60 = self.calculate_wpm(60)

        # update accent color based on 15s WPM (fast feedback)
        new_color = self.get_color_for_wpm(w15)
        if new_color != self.fg_color:
            self.fg_color = new_color

        # apply color to labels
        self.label_15s.config(text=f"15s: {w15} WPM", fg=self.fg_color)
        self.label_30s.config(text=f"30s: {w30} WPM", fg=self.fg_color)
        self.label_60s.config(text=f"60s: {w60} WPM", fg=self.fg_color)

        # append latest sample for graph (we choose to graph 15s instantaneous WPM)
        self.wpm_history.append(w15)
        self.draw_graph()

        self.root.after(SAMPLE_INTERVAL_MS, self.update_ui)

    # ---------- Cleanup ----------
    def close(self):
        # stop listener and destroy window
        try:
            if self.listener and self.listener.running:
                self.listener.stop()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    # optionally allow toggles from environment variables
    if os.getenv("WPM_LOG_KEYS", "0") == "1":
        LOG_KEYS = True
    if os.getenv("WPM_WORDS", "0") == "1":
        COUNT_WORDS_MODE = True

    print("Starting WPM Tracker.")
    if LOG_KEYS:
        print("Key logging enabled -> keys.log")
    if COUNT_WORDS_MODE:
        print("Word-count mode enabled: counting completed words on space/enter.")
    else:
        print("Keystroke-count mode: counting printable characters + spaces/enter.")

    try:
        app = WPMTracker()
        app.run()
    except Exception as e:
        print("Fatal error:", e)
        sys.exit(1)
