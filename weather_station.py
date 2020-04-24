#!/usr/bin/python
# coding=utf-8

import os.path
import time
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import traceback
import epd4in2
import yr
import logger
import socket

font_smallest = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 12)
font_small = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 16)
font_med = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 24)
font_big = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 32)
font_biggest = ImageFont.truetype("/usr/share/fonts/truetype/lato/Lato-Regular.ttf", 48)

def print_weather():
	try:
		data = yr.get_forecast()
		draw_weather(data)

	except:
		draw_error("Sjekk log.txt\nIP: " + get_host_ip())

def draw_weather(data):
	# Get current weather
	weather_now = data[0]

	icon_now = weather_now["icon"]["var"]
	icon_name_now = weather_now["icon"]["text"]

	temperature_val_now = weather_now["temperature"]["val"]
	temperature_unit_now = weather_now["temperature"]["unit"]

	wind_speed_now = weather_now["wind_speed"]["speed"]
	wind_name_now = weather_now["wind_speed"]["name"]
	wind_direction_now = weather_now["wind_direction"]["direction"]

	pressure_val_now = weather_now["pressure"]["val"]
	pressure_unit_now = weather_now["pressure"]["unit"]

	# Get future weather 1
	weather1 = data[1]

	time_1 = weather1["time"]

	icon_1 = weather1["icon"]["var"]
	icon_name_1 = weather1["icon"]["text"]

	temperature_val_1 = weather1["temperature"]["val"]
	temperature_unit_1 = weather1["temperature"]["unit"]

	wind_speed_1 = weather1["wind_speed"]["speed"]

	# Get future weather 2
	weather2 = data[2]

	time_2 = weather2["time"]

	icon_2 = weather2["icon"]["var"]
	icon_name_2 = weather2["icon"]["text"]

	temperature_val_2 = weather2["temperature"]["val"]
	temperature_unit_2 = weather2["temperature"]["unit"]

	wind_speed_2 = weather2["wind_speed"]["speed"]

	# Get credits
	credits = yr.get_credits()

	# Initialize E-Ink screen
	epd = epd4in2.EPD()
	epd.init()
	epd.Clear(0xFF)

	print("Drawing weather report...")
	logger.log("Drawing weather report")

	#Initialize image
	image = Image.new("1", (epd4in2.EPD_WIDTH, epd4in2.EPD_HEIGHT), 255)

	draw = ImageDraw.Draw(image)

	# Draw current weather
	# Weather icon
	icon = Image.open("icons/%s.bmp" % (icon_now))
	image.paste(icon, (5, 5))
	# Temperature
	draw.text((130, 15), u"%s° %s" % (temperature_val_now, temperature_unit_now), font = font_biggest, fill = 0)
	# Cloudiness text
	draw.text((15, 95), icon_name_now, font = font_big, fill = 0)
	# Wind
	draw.text((300, 10), "%s" % (wind_name_now), font = font_small, fill = 0)
	draw.text((300, 30), "%s" % (wind_speed_now), font = font_small, fill = 0)
	draw.text((300, 50), "%s" % (wind_direction_now), font = font_small, fill = 0)
	# Pressure
	draw.text((300, 70), "%s %s" % (pressure_val_now, pressure_unit_now), font = font_small, fill = 0)

	# Draw separator
	draw.line((10, 150, 390, 150), fill = 0)

	# Draw future weather 1
	# Time
	draw.text((20, 160), time_1, font = font_small, fill = 0)
	# Weather icon
	icon1 = Image.open("icons/small/%s.bmp" % (icon_1))
	image.paste(icon1, (20, 180))
	# Temperature
	draw.text((80, 175), u"%s° %s" % (temperature_val_1, temperature_unit_1), font = font_med, fill = 0)
	# Wind
	draw.text((80, 200), "%s" % (wind_speed_1), font = font_small, fill = 0)

	# Draw future weather 2
	# Time
	draw.text((200, 160), time_2, font = font_small, fill = 0)
	# Weather icon
	icon2 = Image.open("icons/small/%s.bmp" % (icon_2))
	image.paste(icon2, (200, 180))
	# Temperature
	draw.text((260, 175), u"%s° %s" % (temperature_val_2, temperature_unit_2), font = font_med, fill = 0)
	# Wind
	draw.text((260, 200), "%s" % (wind_speed_2), font = font_small, fill = 0)

	# Draw separator
	draw.line((10, 235, 390, 235), fill = 0)

	# Credits
	draw.text((15, 240), credits[0], font = font_small, fill = 0)
	draw.text((15, 260), credits[1], font = font_small, fill = 0)
	# Last updated + IP
	draw.text((15, 280), "Sist oppdatert %s | IP: %s" % (datetime.now(), get_host_ip()), font = font_smallest, fill = 0)

	# Draw weather report
	epd.display(epd.getbuffer(image))
	time.sleep(2)
	epd.sleep()

def draw_error(err_msg):
	logger.log("traceback.format_exc():\n" + traceback.format_exc())

	epd = epd4in2.EPD()
	epd.init()
	epd.Clear(0xFF)

	#Initialize image
	image = Image.new("1", (epd4in2.EPD_WIDTH, epd4in2.EPD_HEIGHT), 255)
	draw = ImageDraw.Draw(image)
	draw.text((10, 100), "Noe gikk galt :(", font = font_biggest, fill = 0)
	draw.text((10, 170), err_msg, font = font_med, fill = 0)

	# Draw error message
	epd.display(epd.getbuffer(image))
	time.sleep(2)
	epd.sleep()

	exit()

def get_host_ip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		s.connect(("10.255.255.255", 1)) # Unreachable. It works, so hey!
		IP = s.getsockname()[0]
	except:
		IP = "Ukjent"
	finally:
		s.close()

	return IP

print_weather()
