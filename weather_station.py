#!/usr/bin/python
# coding=utf-8

import os.path
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import traceback
import include.epd5in65f as epd4in2
import include.yr as yr
import include.logger as logger
import socket

font_smallest = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 12)
font_small = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 16)
font_med = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 24)
font_big = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 32)
font_biggest = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 48)


def print_weather():
    try:
        weather_data = yr.get_forecast()
        print("Creating weather report...")
        logger.log("Creating weather report")
        draw_weather(weather_data)

    except Exception as e:
        draw_error("%s\nIP: %s" % (e, get_host_ip()))


def draw_weather(weather_data):
    # Get weather
    logger.log("Reading weather data...")
    weather_future1 = weather_data["weather_future1"]
    weather_future2 = weather_data["weather_future2"]

    # Get credits
    yr_credits = yr.get_credits()

    # Initialize E-Ink screen
    logger.log("Initializing E-ink screen...")
    epd = epd4in2.EPD()
    epd.init()
    epd.Clear()

    # Initialize image
    logger.log("Initializing weather report...")
    image = Image.new("1", (epd4in2.EPD_WIDTH, epd4in2.EPD_HEIGHT), 255)

    draw = ImageDraw.Draw(image)

    # Draw weather in location 1
    draw.text((15, 10), weather_data["name1"], font=font_small, fill=0)
    future1_item = 0
    while future1_item < len(weather_future1):
        draw_future_weather(weather_future1[future1_item], image, future1_item, 30)
        future1_item += 1

    # Draw separator
    draw.line((10, 120, 390, 120), fill=0)

    # Draw weather in location 2
    draw.text((15, 130), weather_data["name2"], font=font_small, fill=0)
    future2_item = 0
    while future2_item < len(weather_future2):
        draw_future_weather(weather_future2[0], image, future2_item, 140)
        future2_item += 1

    # Draw separator
    draw.line((10, 235, 390, 235), fill=0)

    # Credits
    draw.text((15, 240), yr_credits[0], font=font_small, fill=0)
    draw.text((15, 260), yr_credits[1], font=font_small, fill=0)
    # Last updated + IP
    draw.text((15, 280), "Sist oppdatert %s | IP: %s" % (datetime.now(), get_host_ip()), font=font_smallest, fill=0)

    # Draw weather report
    print("Drawing weather report...")
    logger.log("Drawing weather report")
    epd.display(epd.getbuffer(image))
    time.sleep(2)
    epd.sleep()


def draw_future_weather(weather_data, image, pos, y):  # pos starts at 0
    draw = ImageDraw.Draw(image)

    # y positions for future weather are all the same
    future_time_y = y
    future_icon_y = y + 20
    future_temperature_y = y + 70

    # x positions all have the same offset
    x_offset = 80

    # Draw weather
    future_x = 15 + x_offset * pos
    # Time
    draw.text((future_x, future_time_y), weather_data["time"], font=font_small, fill=0)
    # Weather icon
    icon1 = Image.open("icons/small/%s.bmp" % (weather_data["icon"]))
    image.paste(icon1, (future_x, future_icon_y))
    # Temperature
    temperature_text = u"%.1f° C" % (weather_data["temperature"])
    draw.text((future_x + 5, future_temperature_y), temperature_text.replace(".", ","), font=font_smallest,
              fill=0)


def draw_error(err_msg):
    logger.log("traceback.format_exc():\n" + traceback.format_exc())

    epd = epd4in2.EPD()
    epd.init()
    epd.Clear()

    # Initialize image
    image = Image.new("1", (epd4in2.EPD_WIDTH, epd4in2.EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    draw.text((10, 10), "Noe gikk galt :(", font=font_biggest, fill=0)
    draw.text((10, 100), err_msg, font=font_small, fill=0)

    # Draw error message
    epd.display(epd.getbuffer(image))
    time.sleep(2)
    epd.sleep()

    exit()


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))  # Unreachable. It works, so hey!
        IP = s.getsockname()[0]
    except:
        IP = "Ukjent"
    finally:
        s.close()

    return IP


print_weather()
