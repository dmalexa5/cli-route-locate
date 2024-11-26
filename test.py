from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key


import asyncio

ctrl_pressed = False
shift_pressed = False

def on_press(key):
    global ctrl_pressed, shift_pressed
    try:
        if key == Key.ctrl_l or key == Key.ctrl_r:
            ctrl_pressed = True
            print('ctrl pressed')
        elif key == Key.shift:
            shift_pressed = True
            print('shift pressed')
        
        if key == Key.enter and ctrl_pressed and shift_pressed:
            print('Running macro...')
            print(ctrl_pressed, shift_pressed)

    except AttributeError:
        pass

def on_release(key):
    global ctrl_pressed, shift_pressed
    try:
        if key == Key.ctrl_l or key == Key.ctrl_r:
            ctrl_pressed = False
            print('ctrl released')
        elif key == Key.shift:
            shift_pressed = False
            print('shift released')
    except AttributeError:
        pass
    
async def listenKeyboard():
	with KeyboardListener(on_press=on_press,on_release=on_release) as keyboard_listener:
	   keyboard_listener.join()

async def main():
    await asyncio.gather(listenKeyboard())

asyncio.run(main())