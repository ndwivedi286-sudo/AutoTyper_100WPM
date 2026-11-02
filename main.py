import tkinter as tk
from tkinter import messagebox
import threading
import time

try:
    import pyautogui
    import keyboard
except ImportError:
    raise SystemExit("Please run: pip install -r requirements.txt")

pyautogui.PAUSE = 0.001

class AutoTyper:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Typer • 100 WPM")
        self.root.geometry("650x520")
        self.root.minsize(520, 420)

        self.running = False
        self.paused = False
        self.text = ""
        self.index = 0
        self.thread = None

        tk.Label(root, text="⚡ Auto Typer", font=("Segoe UI", 22, "bold")).pack(pady=(18, 4))
        tk.Label(root, text="Text paste karo → target app me cursor rakho → F8 dabao",
                 font=("Segoe UI", 10)).pack(pady=(0, 12))

        self.textbox = tk.Text(root, height=12, font=("Segoe UI", 11), wrap="word")
        self.textbox.pack(fill="both", expand=True, padx=18)

        controls = tk.Frame(root)
        controls.pack(pady=12)

        tk.Label(controls, text="Speed (WPM):").grid(row=0, column=0, padx=5)
        self.speed = tk.IntVar(value=100)
        tk.Spinbox(controls, from_=1, to=300, textvariable=self.speed,
                   width=7, font=("Segoe UI", 11)).grid(row=0, column=1, padx=5)

        self.start_btn = tk.Button(controls, text="F8  Start", width=12,
                                   command=self.start)
        self.start_btn.grid(row=0, column=2, padx=5)

        self.pause_btn = tk.Button(controls, text="F9  Pause", width=12,
                                   command=self.toggle_pause, state="disabled")
        self.pause_btn.grid(row=0, column=3, padx=5)

        self.stop_btn = tk.Button(controls, text="F10  Stop", width=12,
                                  command=self.stop, state="disabled")
        self.stop_btn.grid(row=0, column=4, padx=5)

        self.status = tk.StringVar(value="Ready • F8 = Start")
        tk.Label(root, textvariable=self.status, font=("Segoe UI", 11)).pack(pady=5)

        tk.Label(root, text="IMPORTANT: Start karne ke baad 2 seconds me target app par click karo.",
                 fg="#b45309", font=("Segoe UI", 10, "bold")).pack(pady=(2, 12))

        # Global hotkeys work even when another app is focused.
        keyboard.add_hotkey("f8", self.start)
        keyboard.add_hotkey("f9", self.toggle_pause)
        keyboard.add_hotkey("f10", self.stop)

        root.protocol("WM_DELETE_WINDOW", self.close)

    def get_delay(self):
        wpm = max(1, min(300, int(self.speed.get())))
        # Standard typing estimate: 1 word = 5 characters.
        return 60.0 / (wpm * 5)

    def start(self):
        if self.running:
            return

        text = self.textbox.get("1.0", "end-1c")
        if not text:
            self.root.after(0, lambda: messagebox.showwarning("No text", "Pehle text paste karo."))
            return

        self.text = text
        self.index = 0
        self.running = True
        self.paused = False

        self.root.after(0, self.update_buttons)
        self.root.after(0, lambda: self.status.set("Starting... 2 seconds remaining"))

        # Give the user time to switch to target app.
        self.thread = threading.Thread(target=self.type_worker, daemon=True)
        self.thread.start()

    def type_worker(self):
        time.sleep(2)

        while self.running and self.index < len(self.text):
            if self.paused:
                time.sleep(0.05)
                continue

            ch = self.text[self.index]

            # pyautogui.write handles normal ASCII characters.
            # For Unicode, clipboard paste is used one character at a time.
            try:
                if ord(ch) < 128:
                    pyautogui.write(ch)
                else:
                    # Unicode characters are inserted through clipboard.
                    # Requires pyperclip.
                    import pyperclip
                    old = pyperclip.paste()
                    pyperclip.copy(ch)
                    pyautogui.hotkey("ctrl", "v")
                    time.sleep(0.01)
                    pyperclip.copy(old)
            except Exception:
                pyautogui.write(ch, interval=0)

            self.index += 1
            if self.index % 10 == 0:
                self.root.after(0, self.update_progress)

            time.sleep(self.get_delay())

        if self.running:
            self.running = False
            self.root.after(0, lambda: self.status.set("✓ Completed"))
            self.root.after(0, self.update_buttons)

    def toggle_pause(self):
        if not self.running:
            return
        self.paused = not self.paused
        self.root.after(0, lambda: self.status.set("⏸ Paused" if self.paused else "▶ Typing..."))
        self.root.after(0, self.update_buttons)

    def stop(self):
        self.running = False
        self.paused = False
        self.root.after(0, lambda: self.status.set("■ Stopped"))
        self.root.after(0, self.update_buttons)

    def update_progress(self):
        pct = int((self.index / max(1, len(self.text))) * 100)
        state = "Paused" if self.paused else "Typing"
        self.status.set(f"{state} • {pct}% • {self.index}/{len(self.text)} characters")

    def update_buttons(self):
        active = self.running
        self.start_btn.config(state="disabled" if active else "normal")
        self.pause_btn.config(state="normal" if active else "disabled",
                              text="▶ Resume" if self.paused else "F9  Pause")
        self.stop_btn.config(state="normal" if active else "disabled")

    def close(self):
        self.running = False
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    AutoTyper(root)
    root.mainloop()
