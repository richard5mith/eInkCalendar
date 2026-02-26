#!/usr/bin/python3
import locale
import logging
import os
import sys
import time
import re
from datetime import datetime

import schedule
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.Image import Image as TImage
from PIL.ImageDraw import ImageDraw as TImageDraw

import lib.epd7in5b_V2 as eInk
from dataHelper import get_events
from displayHelpers import *
from settings import LOCALE, ROTATE_IMAGE

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    handlers=[logging.FileHandler(filename="info.log", mode='w'),
                    logging.StreamHandler()])
logger = logging.getLogger('app')

CURRENT_DICT = os.path.dirname(os.path.realpath(__file__))
PICTURE_DICT = os.path.join(CURRENT_DICT, 'pictures')
FONT_DICT = os.path.join(CURRENT_DICT, 'fonts')

DEBUG = False

FONT_ROBOTO_DATE = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 200)
FONT_ROBOTO_H1 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 40)
FONT_ROBOTO_H2 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 30)
FONT_ROBOTO_P = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 30)
FONT_POPPINS_BOLT_P = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Poppins-Bold.ttf'), 22)
FONT_POPPINS_P = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Poppins-Regular.ttf'), 30)
LINE_WIDTH = 3


def main():
    logger.info(datetime.now())
    try:
        epd = eInk.EPD()

        if DEBUG:
            logger.info("DEBUG-Mode activated...")

        image_blk = Image.open(os.path.join(
            PICTURE_DICT, "blank-hk.bmp"))
        image_red = Image.open(os.path.join(
            PICTURE_DICT, "blank-hk.bmp"))

        draw_blk = ImageDraw.Draw(image_blk)
        draw_red = ImageDraw.Draw(image_red)

        render_content(draw_blk, image_blk, draw_red,
                       image_red, epd.width, epd.height)
        show_content(epd, image_blk, image_red)
        # clear_content(epd)

    except Exception as e:
        logger.warning(e)
        if not DEBUG:
            logger.info("Trying to module_exit()")
            eInk.epdconfig.module_exit()
        raise e


def ordinal(n: int) -> str:
    suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10 if n % 100 not in (11, 12, 13) else 0, 'th')
    return f"{n}{suffix}"


def render_content(draw_blk: TImageDraw, image_blk: TImage,  draw_red: TImageDraw, image_red: TImage, height: int, width: int):
    locale.setlocale(locale.LC_ALL, LOCALE)

    PADDING_TOP = int(height/100)
    MARGIN_X = int(width * 0.22)   # x position of the vertical margin line
    MARGIN_GAP = int(width/60)     # gap on the left side of line
    MARGIN_GAP_RIGHT = int(width/20)  # gap on the right side of line before text
    now = time.localtime()
    day_str = time.strftime("%A")
    day_number = now.tm_mday
    month_str = time.strftime("%B")

    # Vertical margin line — full screen height
    draw_red.line((MARGIN_X, 0, MARGIN_X, height), fill=1, width=LINE_WIDTH)

    # Heading — right of the line
    current_height = height/20
    draw_red.text((MARGIN_X + MARGIN_GAP_RIGHT, current_height), day_str.upper(),
                  font=FONT_ROBOTO_H1, fill=1)
    current_height += get_font_height(FONT_ROBOTO_H1) + PADDING_TOP
    draw_red.text((MARGIN_X + MARGIN_GAP_RIGHT, current_height), "{} {}".format(month_str.upper(), day_number),
                  font=FONT_ROBOTO_H1, fill=1)
    current_height += get_font_height(FONT_ROBOTO_H1)

    # Calendar
    current_height += height/40
    event_list = get_events(10)

    from devtools import debug

    last_event_day = datetime.now().date()
    for event in event_list:
        # Draw new day header — right of the line
        if last_event_day != event.start.date():
            current_height += get_font_height(FONT_POPPINS_P) * 0.6
            last_event_day = event.start.date()
            day_string = "{} {}".format(last_event_day.strftime("%a"), ordinal(last_event_day.day))
            draw_blk.text((MARGIN_X + MARGIN_GAP_RIGHT, current_height),
                          day_string, font=FONT_ROBOTO_P, fill=1)
            current_height += get_font_height(FONT_ROBOTO_P)

        # Draw time right-aligned into the margin
        if event.all_day:
            time_str = "· · ·"
        else:
            time_str = event.start.strftime("%H:%M")
        time_width = get_font_width(FONT_POPPINS_P, time_str)
        draw_blk.text((MARGIN_X - MARGIN_GAP - time_width, current_height),
                      time_str, font=FONT_POPPINS_P, fill=1)

        # Draw summary left-aligned from the margin line
        debug(event.summary)
        event.summary = re.sub(r'[^\x00-\x7f]', r'', event.summary).strip()
        draw_blk.text((MARGIN_X + MARGIN_GAP_RIGHT, current_height), event.summary,
                      font=FONT_POPPINS_P, fill=1)
        current_height += get_font_height(FONT_POPPINS_P) * 1.1


def show_content(epd: eInk.EPD, image_blk: TImage, image_red: TImage):
    logger.info("Exporting finial images")
    image_blk.save("EXPORT-black.bmp")
    image_red.save("EXPORT-red.bmp")
    if ROTATE_IMAGE:
        image_blk = image_blk.rotate(180)
        image_red = image_red.rotate(180)
    if not DEBUG:
        init_display(epd)
        logger.info("Writing on display")
        epd.display(epd.getbuffer(image_blk), epd.getbuffer(image_red))
        set_sleep(epd)


def clear_content(epd: eInk.EPD):
    if DEBUG:
        logger.warning("Clear has no effect while debugging")
    else:
        init_display(epd)
        clear_display(epd)
        set_sleep(epd)


if __name__ == '__main__':
    main()
