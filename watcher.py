from pynput.keyboard import Key, KeyCode
from pynput.keyboard import Listener as KeyboardListener
from pynput import keyboard
import threading, rich


class Watcher:
    def __init__(self, func, kwargs):
        self.func = func
        self.kwargs = kwargs
        self.ctrl_pressed = False
        self.listener = None

    def on_press(self, key:Key):

        try:
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self.ctrl_pressed = True

            elif key == Key.shift:
                self.shift_pressed = True
            
            elif key == Key.right and self.ctrl_pressed and self.shift_pressed: # \x12 is the ASCII code for 'r' i think
                rich.print(f'\nRunning macro: [bold cyan]{getattr(self.func, "__name__", "unknown")}[/bold cyan]...')

                self.func(**self.kwargs)

                self.ctrl_pressed = False
                self.shift_pressed = False
                self.stop()
                return

        except AttributeError:
            pass

    def on_release(self, key):
        try:
            if key == Key.ctrl_l or key == Key.ctrl_r:
                self.ctrl_pressed = False

            elif key == Key.shift:
                self.shift_pressed = False

        except AttributeError:
            pass

    def start(self):
        self.listener = KeyboardListener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()
        self.listener.join()

    def stop(self):
        if self.listener:
            self.listener.stop()

