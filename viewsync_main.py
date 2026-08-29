import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import os
import json

CONFIG_FILE = os.path.join(os.path.expanduser('~'), '.viewsync_profiles.json')
OLD_CONFIG = os.path.join(os.path.expanduser('~'), '.viewsync_crop.txt')

# ─── Color Palette ───
BG          = "#1e1e2e"
SURFACE     = "#2a2a3d"
CARD        = "#313146"
ACCENT      = "#7c3aed"
ACCENT_HVR  = "#9b59f0"
GREEN       = "#22c55e"
GREEN_HVR   = "#16a34a"
BLUE        = "#3b82f6"
BLUE_HVR    = "#2563eb"
RED         = "#ef4444"
RED_HVR     = "#dc2626"
TEXT        = "#e2e8f0"
TEXT_DIM    = "#94a3b8"
SLIDER_BG   = "#3f3f5a"

def styled_btn(parent, text, bg_color, hover_color, command, font_size=11, pady=8):
    b = tk.Button(parent, text=text, bg=bg_color, fg="white", activebackground=hover_color,
                  activeforeground="white", font=("Segoe UI", font_size, "bold"),
                  relief="flat", bd=0, cursor="hand2", command=command, pady=pady)
    b.bind("<Enter>", lambda e: b.config(bg=hover_color))
    b.bind("<Leave>", lambda e: b.config(bg=bg_color))
    return b

class ScrcpyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ViewSync Master v1.0.0")
        self.root.geometry("460x680")
        self.root.configure(bg=BG)
        self.root.minsize(400, 500)

        self.process = None
        self.profiles = {}
        self.current_profile = tk.StringVar()
        self.enable_kb_var = tk.BooleanVar(value=False)
        self.val_l = tk.IntVar(value=0)
        self.val_r = tk.IntVar(value=0)
        self.val_t = tk.IntVar(value=0)
        self.val_b = tk.IntVar(value=0)
        self._status_timer = None

        self.load_profiles()
        self.build_ui()
        self.on_profile_select(None)

    def load_profiles(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    self.profiles = json.load(f)
            except:
                pass
        if not self.profiles:
            self.profiles = {"Physics Wallah": {"L": 0, "R": 0, "T": 0, "B": 0}}
            if os.path.exists(OLD_CONFIG):
                try:
                    with open(OLD_CONFIG, 'r') as f:
                        l, r, t, b = map(int, f.read().strip().split(','))
                        self.profiles["Physics Wallah"] = {"L": l, "R": r, "T": t, "B": b}
                except:
                    pass
            self.save_profiles()
        self.current_profile.set(list(self.profiles.keys())[0])

    def save_profiles(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.profiles, f, indent=4)

    def show_status(self, msg, color=GREEN):
        self.status_lbl.config(text=msg, fg=color, bg="#1a3a1a" if color == GREEN else "#3a1a1a" if color == RED else SURFACE)
        if self._status_timer:
            self.root.after_cancel(self._status_timer)
        self._status_timer = self.root.after(3000, lambda: self.status_lbl.config(text="Ready", fg=TEXT_DIM, bg=SURFACE))

    def build_ui(self):
        title_bar = tk.Frame(self.root, bg=ACCENT, height=50)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        tk.Label(title_bar, text="⚡ ViewSync Master v1.0.0", bg=ACCENT, fg="white", font=("Segoe UI", 14, "bold")).pack(side=tk.LEFT, padx=15, pady=10)

        container = tk.Frame(self.root, bg=BG)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

        self._card(container, "📁  PROFILES", self._build_profile_card)
        self._card(container, "✂️  CROP SETTINGS", self._build_crop_card)
        self._card(container, "🚀  LAUNCH", self._build_launch_card)

        status_frame = tk.Frame(self.root, bg=SURFACE, height=32)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        self.status_lbl = tk.Label(status_frame, text="Ready", bg=SURFACE, fg=TEXT_DIM, font=("Segoe UI", 10), anchor="w", padx=15)
        self.status_lbl.pack(fill=tk.BOTH, expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _card(self, parent, title, builder):
        outer = tk.Frame(parent, bg=CARD, highlightbackground="#404060", highlightthickness=1)
        outer.pack(fill=tk.X, pady=6)
        header = tk.Frame(outer, bg=CARD)
        header.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(header, text=title, bg=CARD, fg=TEXT_DIM, font=("Segoe UI", 9, "bold")).pack(anchor=tk.W)
        body = tk.Frame(outer, bg=CARD)
        body.pack(fill=tk.X, padx=12, pady=(5, 12))
        builder(body)

    def _build_profile_card(self, parent):
        row1 = tk.Frame(parent, bg=CARD)
        row1.pack(fill=tk.X, pady=(0, 8))
        tk.Label(row1, text="Active:", bg=CARD, fg=TEXT, font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.profile_cb = ttk.Combobox(row1, textvariable=self.current_profile, state="readonly", width=28, font=("Segoe UI", 10))
        self.profile_cb['values'] = list(self.profiles.keys())
        self.profile_cb.pack(side=tk.LEFT, padx=(8, 0), fill=tk.X, expand=True)
        self.profile_cb.bind('<<ComboboxSelected>>', self.on_profile_select)

        row2 = tk.Frame(parent, bg=CARD)
        row2.pack(fill=tk.X)
        for txt, cmd in [("➕ New", self.new_profile), ("💾 Save", self.save_current_profile),
                          ("✏️ Rename", self.rename_profile), ("🗑️ Delete", self.delete_profile)]:
            b = tk.Button(row2, text=txt, bg=SURFACE, fg=TEXT, font=("Segoe UI", 9, "bold"),
                          relief="flat", padx=8, pady=5, cursor="hand2", command=cmd,
                          activebackground=ACCENT, activeforeground="white", bd=0)
            b.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)

    def _build_crop_card(self, parent):
        for label, var in [("Left", self.val_l), ("Right", self.val_r),
                           ("Top", self.val_t), ("Bottom", self.val_b)]:
            self._slider_row(parent, label, var)

    def _slider_row(self, parent, label, var):
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill=tk.X, pady=3)
        tk.Label(row, text=label, bg=CARD, fg=TEXT, width=7, anchor="w", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        scale = tk.Scale(row, from_=0, to=500, orient=tk.HORIZONTAL, variable=var,
                         bg=CARD, fg=TEXT, troughcolor=SLIDER_BG, highlightthickness=0,
                         activebackground=ACCENT, sliderrelief="flat", showvalue=False, sliderlength=18, bd=0)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10))
        val_lbl = tk.Label(row, text="0", bg=SURFACE, fg=ACCENT, width=4, font=("Segoe UI", 10, "bold"), padx=4, pady=2)
        val_lbl.pack(side=tk.RIGHT)
        def update_lbl(*args):
            val_lbl.config(text=str(var.get()))
        var.trace_add("write", update_lbl)
        update_lbl()

    def _build_launch_card(self, parent):
        cb = tk.Checkbutton(parent, text="⌨️ Allow typing from Laptop Keyboard (May trigger polls with Spacebar)", variable=self.enable_kb_var, bg=CARD, fg=TEXT, selectcolor=BG, activebackground=CARD, activeforeground=TEXT, font=("Segoe UI", 9))
        cb.pack(anchor=tk.W, pady=(0, 8))
        b1 = styled_btn
        b1 = styled_btn(parent, "▶  Normal Phone  (Bina Crop Ke)", ACCENT, ACCENT_HVR, self.launch_normal, font_size=12, pady=10)
        b1.pack(fill=tk.X, pady=(0, 8))
        row = tk.Frame(parent, bg=CARD)
        row.pack(fill=tk.X, pady=(0, 8))
        b2 = styled_btn(row, "🖥  Cropped Fullscreen", GREEN, GREEN_HVR, lambda: self.launch_cropped(True), font_size=10, pady=8)
        b2.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        b3 = styled_btn(row, "🔍  Preview Window", BLUE, BLUE_HVR, lambda: self.launch_cropped(False), font_size=10, pady=8)
        b3.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
        b4 = styled_btn(parent, "■  Stop ViewSync", RED, RED_HVR, self.stop_viewsync, font_size=10, pady=8)
        b4.pack(fill=tk.X)

    def on_profile_select(self, event):
        p = self.current_profile.get()
        if p in self.profiles:
            v = self.profiles[p]
            self.val_l.set(v.get("L", 0))
            self.val_r.set(v.get("R", 0))
            self.val_t.set(v.get("T", 0))
            self.val_b.set(v.get("B", 0))

    def _refresh_cb(self):
        self.profile_cb['values'] = list(self.profiles.keys())

    def new_profile(self):
        name = simpledialog.askstring("New Profile", "Profile ka naam daalein:")
        if name and name.strip():
            name = name.strip()
            if name in self.profiles:
                self.show_status(f"❌ '{name}' pehle se exist karta hai!", RED)
                return
            self.profiles[name] = {"L": self.val_l.get(), "R": self.val_r.get(), "T": self.val_t.get(), "B": self.val_b.get()}
            self.save_profiles()
            self.current_profile.set(name)
            self._refresh_cb()
            self.show_status(f"✅ Profile '{name}' created!")

    def save_current_profile(self):
        p = self.current_profile.get()
        self.profiles[p] = {"L": self.val_l.get(), "R": self.val_r.get(), "T": self.val_t.get(), "B": self.val_b.get()}
        self.save_profiles()
        self.show_status(f"✅ Profile '{p}' saved! (L:{self.val_l.get()} R:{self.val_r.get()} T:{self.val_t.get()} B:{self.val_b.get()})")

    def rename_profile(self):
        old = self.current_profile.get()
        new = simpledialog.askstring("Rename", f"'{old}' ka naya naam:")
        if new and new.strip() and new.strip() != old:
            new = new.strip()
            if new in self.profiles:
                self.show_status(f"❌ '{new}' pehle se hai!", RED)
                return
            self.profiles[new] = self.profiles.pop(old)
            self.save_profiles()
            self.current_profile.set(new)
            self._refresh_cb()
            self.show_status(f"✅ Renamed to '{new}'")

    def delete_profile(self):
        p = self.current_profile.get()
        if len(self.profiles) <= 1:
            self.show_status("❌ Aakhri profile delete nahi kar sakte!", RED)
            return
        if messagebox.askyesno("Delete?", f"Kya '{p}' delete karein?"):
            del self.profiles[p]
            self.save_profiles()
            self.current_profile.set(list(self.profiles.keys())[0])
            self._refresh_cb()
            self.on_profile_select(None)
            self.show_status(f"🗑️ Profile '{p}' deleted")

        subprocess.Popen("if ! pgrep -f viewsync_helper.py > /dev/null; then nohup python3 ~/.viewsync/viewsync_helper.py > /dev/null 2>&1 & fi", shell=True)

    def launch_normal(self):
        self.stop_viewsync()
        # Added -b 4M --max-fps 30 for smooth playback
        kb_flag = [] if self.enable_kb_var.get() else ["--keyboard=disabled"]
        cmd = ["/usr/local/bin/scrcpy", "--window-title=viewsync"] + kb_flag + ["-m", "1024", "-b", "2M", "--max-fps", "30"]
        env = os.environ.copy()
        env["ADB"] = "/usr/bin/adb"
        self.process = subprocess.Popen(cmd, env=env)
        self.show_status("▶ ViewSync launched (Normal Mode - Smooth)")

    def launch_cropped(self, fullscreen):
        self.stop_viewsync()
        p = self.current_profile.get()
        self.profiles[p] = {"L": self.val_l.get(), "R": self.val_r.get(), "T": self.val_t.get(), "B": self.val_b.get()}
        self.save_profiles()

        v = self.profiles[p]
        L, R, T, B = v["L"], v["R"], v["T"], v["B"]
        PW = 1080 - T - B
        PH = 2280 - L - R
        crop = f"{PW}:{PH}:{B}:{L}"
        
        # Added -b 4M --max-fps 30 for smooth playback
        kb_flag = [] if self.enable_kb_var.get() else ["--keyboard=disabled"]
        cmd = ["/usr/local/bin/scrcpy", "--window-title=viewsync"] + kb_flag + ["--crop", crop, "-m", "1024", "-b", "2M", "--max-fps", "30"]
        if fullscreen:
            cmd.append("-f")
        env = os.environ.copy()
        env["ADB"] = "/usr/bin/adb"
        self.process = subprocess.Popen(cmd, env=env)
        mode = "Fullscreen" if fullscreen else "Windowed"
        self.show_status(f"▶ ViewSync launched ({mode} - Smooth) — Profile: {p}")

    def stop_viewsync(self):
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=2)
            except:
                self.process.kill()
            self.process = None
        subprocess.run(["pkill", "-f", "viewsync_helper.py"]); import time; time.sleep(0.5)

    def on_close(self):
        self.stop_viewsync()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScrcpyApp(root)
    root.mainloop()
