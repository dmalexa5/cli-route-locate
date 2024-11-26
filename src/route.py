from pynput import keyboard, mouse
from time import sleep
import re, rich, yaml
from pynput.keyboard import Listener as KeyboardListener
from pynput.keyboard import Key
from watcher import Watcher

with open('../config/messages.yml', 'r') as f:
    messages = yaml.load(f, Loader=yaml.Loader)

def route_part(kb:keyboard.Controller, pn:str, records:list) -> None:

    sleep(1.5) #TODO: Wait for ctrl + shift + enter to be released
    kb.type(pn + '\t'*7)    

    # Enter records into oracle
    for record in records:
        enter_record(kb, record)

def enter_record(kb:keyboard.Controller, record:list):
    '''Routine for entering a record when the first sequence box is highlighted.'''

    seq = record[0]
    cell = record[1]
    resource = record[2]
    usage = record[3]
    description = record[-1]

    kb.type(f"{seq}\t\t\t{cell}\r")
    kb.type(f"{seq}\t{resource}\t\t\t{usage}\t")
    close_oracle_window(kb)
    kb.type('\t'*18 + description)
    ctrl_key(kb, 's')
    kb.press(keyboard.Key.down)
    kb.release(keyboard.Key.down)
    pass



def enter_locator_pn(kb:keyboard.Controller, pn:str) -> None:
    '''Macro.
    Assumes that this is run when user ctrl + clicks into zoom find item box.'''

    sleep(1.25) #TODO: Wait for ctrl + shift + click to be released

    kb.type(f"{pn}\r\r")
    ctrl_key(kb, keyboard.Key.tab)
    kb.press(keyboard.Key.down); kb.release(keyboard.Key.down)

    return

def enter_locator(kb:keyboard.Controller, locator:str) -> None:
    '''Macro.
    Assumes that this is run when user ctrl + shift + enters in the POU locator box.'''

    sleep(1.25) #TODO: Wait for ctrl + shift + enter to be released

    kb.type(locator)
    ctrl_key(kb, 's')
    ctrl_key(kb, keyboard.Key.tab)
    kb.type(f'\t{locator}')
    ctrl_key(kb, 's') # Save
    alt_key(kb, 'i') # WIP Mass Update

    return


def close_oracle_window(kb:keyboard.Controller):
    ctrl_key(kb, keyboard.Key.f4)

def ctrl_key(kb:keyboard.Controller, key:keyboard.Key):
        '''ctrl + key'''

        try:
            with kb.pressed(keyboard.Key.ctrl):
                kb.press(key)
                kb.release(key)
        except:
            raise KeyError("Invalid key used.")
        
def alt_key(kb:keyboard.Controller, key):
    '''alt + key'''

    try:
        with kb.pressed(keyboard.Key.alt):
            kb.press(key)
            kb.release(key)
    except:
        raise KeyError("Invalid key used.")
    
def route_macro(kb:keyboard.Controller, pn:str, records:list):

    # Routings Macro
    rich.print(messages['route']['routings_item_box'])
    watcher = Watcher(route_part, {'kb':kb, 'pn':pn, 'records':records})
    watcher.start()
    
    sleep(2.5) # Wait for oracle to catch up

    rich.print(messages['route']['routing_complete'])
    return

def locate_macro(kb:keyboard.Controller, pn:str, locator:str):

    # Locator PN Macro / pre-locator prep macro
    rich.print(messages['route']['zoom_item_box'])
    watcher = Watcher(enter_locator_pn, {'kb':kb, 'pn':pn})
    watcher.start()

    sleep(0.5)
    rich.print(messages['route']['zoom_item_complete'])

    # Locator Macro
    rich.print(messages['route']['locator_box'])
    watcher = Watcher(enter_locator, {'kb':kb, 'locator':locator})
    watcher.start()

    sleep(0.5)
    rich.print(messages['route']['locator_complete'])
    return
