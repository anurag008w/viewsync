import subprocess
import time
from pynput import keyboard

def get_active_window_title():
    try:
        window_id = subprocess.check_output(['xdotool', 'getactivewindow']).strip()
        window_name = subprocess.check_output(['xdotool', 'getwindowname', window_id]).decode('utf-8', errors='ignore').strip()
        return window_name.lower()
    except Exception:
        return ""

def on_press(key):
    try:
        title = get_active_window_title()
        if "viewsync" in title:
            if key == keyboard.Key.space:
                subprocess.Popen(["/usr/bin/adb", "shell", "input", "keyevent", "85"])
            elif key == keyboard.Key.right:
                subprocess.Popen(["/usr/bin/adb", "shell", "input", "keyevent", "90"])
            elif key == keyboard.Key.left:
                subprocess.Popen(["/usr/bin/adb", "shell", "input", "keyevent", "89"])
    except Exception as e:
        pass

if __name__ == "__main__":
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()
