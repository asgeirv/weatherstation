#!/usr/bin/python
# coding=utf-8

import os.path
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import traceback
import include.epd4in2 as epd4in2
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

    except:
        draw_error("Sjekk /var/log/weatherstation_log.txt\nIP: " + get_host_ip())


def draw_weather(weather_data):
    # Get current weather
    logger.log("Reading weather data...")
    weather_now = weather_data["weather_now"]
    weather_6 = weather_data["weather_6"]
    weather_12 = weather_data["weather_12"]

    # Get credits
    yr_credits = yr.get_credits()

    # Initialize E-Ink screen
    logger.log("Initializing E-ink screen...")
    epd = epd4in2.EPD()
    epd.init()
    epd.Clear(0xFF)

    # Initialize image
    logger.log("Initializing weather report...")
    image = Image.new("1", (epd4in2.EPD_WIDTH, epd4in2.EPD_HEIGHT), 255)

    draw = ImageDraw.Draw(image)

    # Draw current weather
    # Weather icon
    icon = Image.open("icons/%s.bmp" % (weather_now["icon"]))
    image.paste(icon, (5, 5))
    # Temperature
    draw.text((130, 15), u"%.1f° C" % (weather_now["temperature"]), font=font_biggest, fill=0)
    # Wind
    draw.text((135, 75), "%.1f m/s %s" % (weather_now["wind_speed"], weather_now["wind_direction"]), font=font_med, fill=0)
    # Pressure
    draw.text((135, 105), "%.0f hPa" % (weather_now["pressure"]), font=font_small, fill=0)

    # Draw separator
    draw.line((10, 140, 390, 140), fill=0)

    # Draw weather in 6 hours
    # Time
    draw.text((20, 150), weather_6["time"], font=font_small, fill=0)
    # Weather icon
    icon1 = Image.open("icons/small/%s.bmp" % (weather_6["icon"]))
    image.paste(icon1, (20, 180))
    # Temperature
    draw.text((90, 250), u"%.1f° C" % (weather_6["temperature"]), font=font_smallest, fill=0)

    # Draw weather in 12 hours
    # Time
    draw.text((200, 150), weather_12["time"], font=font_small, fill=0)
    # Weather icon
    icon1 = Image.open("icons/small/%s.bmp" % (weather_12["icon"]))
    image.paste(icon1, (200, 180))
    # Temperature
    draw.text((270, 250), u"%.1f° C" % (weather_12["temperature"]), font=font_smallest, fill=0)

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


def draw_error(err_msg):
    logger.log("traceback.format_exc():\n" + traceback.format_exc())

    epd = epd4in2.EPD()
    epd.init()
    epd.Clear(0xFF)

    # Initialize image
    image = Image.new("1", (epd4in2.EPD_WIDTH, epd4in2.EPD_HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    draw.text((10, 100), "Noe gikk galt :(", font=font_biggest, fill=0)
    draw.text((10, 170), err_msg, font=font_med, fill=0)

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
