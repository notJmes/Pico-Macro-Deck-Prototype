# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2021 ladyada for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense

from random import randint
import board
import busio
import terminalio
import displayio
import digitalio
import time
from adafruit_display_text import label, wrap_text_to_lines, outlined_label
import adafruit_displayio_sh1106

import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS

from fourwire import FourWire
from i2cdisplaybus import I2CDisplayBus

displayio.release_displays()

SCL = board.GP21
SDA = board.GP20

i2c = busio.I2C(SCL, SDA)
display_bus = I2CDisplayBus(
    i2c,
    device_address=0x3C,
)

WIDTH = 132
HEIGHT = 64
BORDER = 0
display = adafruit_displayio_sh1106.SH1106(display_bus, width=WIDTH, height=HEIGHT)

def update_text(text):
    text = '\n'.join(wrap_text_to_lines(text, 20))
    text_area = label.Label(terminalio.FONT, text=text)
    text_area.x = 5
    text_area.y = 5
    display.root_group = text_area

text_area = outlined_label.OutlinedLabel(
    terminalio.FONT,
    text='Click to begin...',
    color=0xFF00FF,
    outline_color=0x00FF00,
    outline_size=1,
    padding_left=2,
    padding_right=2,
    padding_top=2,
    padding_bottom=2,
    scale=1,
)
text_area.anchor_point = (0, 0)
text_area.anchored_position = (10, 10)
display.root_group = text_area


# Buttons

btn1 = digitalio.DigitalInOut(board.GP0)
btn1.switch_to_input(pull=digitalio.Pull.DOWN)

btn2 = digitalio.DigitalInOut(board.GP1)
btn2.switch_to_input(pull=digitalio.Pull.DOWN)

kbd = Keyboard(usb_hid.devices)
def hello():
    txt = 'hello'
    KeyboardLayoutUS(kbd).write(txt)
    return txt

def rand():
    num = randint(0,9)
    KeyboardLayoutUS(kbd).write(str(num))
    return num

def ctrlaltdel():
    kbd.send(Keycode.CONTROL, Keycode.ALT, Keycode.DELETE)
    return 'Getting to start menu'

def hiberate():
    kbd.send(Keycode.WINDOWS, Keycode.R)
    time.sleep(0.1)
    KeyboardLayoutUS(kbd).write('shutdown /h')
    kbd.send(Keycode.ENTER)
    return 'Hibernating...'

text = {'Say Hi': hello,
        'Random number from 0 to 9': rand,
        'CTRL+ALT+DEL': ctrlaltdel,
        'Hiberate PC': hiberate}

pointer = 0
while True:
    if btn1.value:
        pointer = (pointer + 1) % len(text)
        update_text(list(text)[pointer])
    if btn2.value:
        update_text(str(text[list(text)[pointer]]()))
    time.sleep(0.1)