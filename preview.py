#!/usr/bin/python3
"""
Generate EXPORT-black.bmp and EXPORT-red.bmp without touching the display hardware.

Usage:
    python3 preview.py
"""
import sys
from unittest.mock import MagicMock

# Mock hardware libs before any import touches them
for mod in ('lib.epd7in5b_V2', 'lib.epdconfig', 'RPi', 'RPi.GPIO', 'spidev', 'gpiozero'):
    sys.modules[mod] = MagicMock()

import os
from PIL import Image, ImageDraw

import displayRun

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PICTURE_DIR = os.path.join(CURRENT_DIR, 'pictures')

# Match the same argument order as main() -> render_content(... epd.width, epd.height)
# epd.width=800, epd.height=480  =>  height=800, width=480
EPD_WIDTH = 800
EPD_HEIGHT = 480

image_blk = Image.open(os.path.join(PICTURE_DIR, "blank-hk.bmp"))
image_red = Image.open(os.path.join(PICTURE_DIR, "blank-hk.bmp"))

draw_blk = ImageDraw.Draw(image_blk)
draw_red = ImageDraw.Draw(image_red)

displayRun.render_content(draw_blk, image_blk, draw_red, image_red, EPD_WIDTH, EPD_HEIGHT)

image_blk.save("EXPORT-black.bmp")
image_red.save("EXPORT-red.bmp")
print("Saved EXPORT-black.bmp and EXPORT-red.bmp")
