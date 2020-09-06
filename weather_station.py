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
        draw_error("Se /var/log/weatherstation_log.txt\nIP: " + get_host_ip())


def draw_weather(weather_data):
    # Get weather
    logger.log("Reading weather data...")
    weather_now = weather_data["weather_now"]
    weather_future = weather_data["weather_future"]

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
    image.paste(icon, (10, 10))
    # Text box positions are related to one another
    # Temperature
    temperature_x = 130
    temperature_y = 15
    draw.text((temperature_x, temperature_y), u"%.1f° C" % (weather_now["temperature"]), font=font_biggest, fill=0)
    # Wind
    wind_y = temperature_y + 60
    draw.text((temperature_x + 5, wind_y), "%.1f m/s %s" % (weather_now["wind_speed"], weather_now["wind_direction"]), font=font_med, fill=0)
    # Pressure
    draw.text((temperature_x + 5, wind_y + 30), "%.0f hPa" % (weather_now["pressure"]), font=font_small, fill=0)

    # Draw separator
    draw.line((10, 140, 390, 140), fill=0)

    # Draw future weather
    item = 0
    while item < len(weather_future):
        draw_future_weather(weather_future[item], image, item)
        item += 1

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


def draw_future_weather(weather_data, image, pos):  # pos starts at 0
    draw = ImageDraw.Draw(image)

    # y positions for future weather are all the same
    future_time_y = 150
    future_icon_y = 175
    future_temperature_y = 215

    # x positions all have the same offset
    x_offset = 80

    # Draw weather
    future_x = 20 + x_offset * pos
    # Time
    draw.text((future_x, future_time_y), weather_data["time"], font=font_small, fill=0)
    # Weather icon
    icon1 = Image.open("icons/small/%s.bmp" % (weather_data["icon"]))
    draw.paste(icon1, (future_x, future_icon_y))
    # Temperature
    draw.text((future_x + 5, future_temperature_y), u"%.1f° C" % (weather_data["temperature"]), font=font_smallest,
              fill=0)


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
