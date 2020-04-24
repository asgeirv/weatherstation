# coding=utf-8

import requests
import codecs
from datetime import datetime, time
import xml.etree.ElementTree as ET
import configparser
import urllib.parse as urlparser
import logger

def read_config():
	config_parser = configparser.ConfigParser()
	config_parser.readfp(open(r'weather.conf'))

	country = config_parser.get("loc", "country")
	region = config_parser.get("loc", "region")
	municipality = config_parser.get("loc", "municipality")
	location = config_parser.get("loc", "location")

	return (country, region, municipality, location)

def get_weather_data():
	print("Getting weather data from yr.no...")
	(country, region, municipality, location) = read_config()
	url = urlparser.quote("www.yr.no/sted/%s/%s/%s/%s/varsel.xml" % (country, region, municipality, location))
	logger.log("Getting weather data from " + url)
	data = requests.get("http://" + url)
	return data.content.decode("utf-8")

def write_weather_data(weather_data):
	print("Caching weather data...")
	logger.log("Caching weather data")
	with codecs.open("weather.xml", encoding="utf-8", mode="w") as weather_xml:
		weather_xml.write(weather_data)
	weather_xml.closed

def get_xml_root():
	write_weather_data(get_weather_data())
	tree = ET.parse("weather.xml")
	return tree.getroot()

def get_forecast():
	root = get_xml_root()
	# Get forecasts
	forecast = root.find("forecast")
	tabular = forecast.find("tabular")
	data = []

	# Find forecast for current time period
	for period in tabular.findall("time"):
		start_time = period.get("from")
		end_time = period.get("to")
		start_time = to_datetime(start_time)
		end_time = to_datetime(end_time)

		if end_time > datetime.now():
			data.append(get_weather(start_time, period))

	return data

def get_weather(start_time, period):
	# Get weather icon
	symbol = period.find("symbol")
	sym_var = symbol.get("var")
	sym_text = symbol.get("name")
	symbol = {"var": sym_var, "text": sym_text}

	# Get precipitation data
	precipitation = period.find("precipitation")
	val = precipitation.get("value")
	precipitation = {"val": val}

	# Get wind direction
	wind_direction = period.find("windDirection")
	name = wind_direction.get("name")
	wind_direction = {"direction": name.lower()}

	# Get wind speed
	wind_speed = period.find("windSpeed")
	speed = wind_speed.get("mps")
	name = wind_speed.get("name")
	wind_speed = {"speed": speed.replace(".", ",") + " m/s", "name": name}

	# Get temperature
	temperature = period.find("temperature")
	unit = temperature.get("unit")
	val = temperature.get("value")
	temperature = {"unit": unit[0].upper(), "val": val}

	# Get pressure
	pressure = period.find("pressure")
	unit = pressure.get("unit")
	val = pressure.get("value")
	pressure = {"unit": unit, "val": val}

	return {
		"time": start_time.strftime("%H:%M"),
		"icon": symbol,
		"precipitation": precipitation,
		"wind_direction": wind_direction,
		"wind_speed": wind_speed,
		"temperature": temperature,
		"pressure": pressure
		}

def get_credits():
	return [u"Værvarsel fra Yr, ", u"levert av NRK og Meteorologisk institutt"]

def to_datetime(timestamp):
	date, time = timestamp.split("T")
	year, month, day = date.split("-")
	hour, minute, second = time.split(":")

	return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))
