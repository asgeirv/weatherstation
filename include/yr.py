# coding=utf-8

import requests
import codecs
from datetime import datetime, timedelta
import json
import configparser
import include.logger as logger


def read_config():
    config_parser = configparser.ConfigParser()
    config_parser.read_file(open(r'weather.conf'))

    lat = config_parser.get("loc", "lat")
    long = config_parser.get("loc", "long")

    return {"lat": lat, "long": long}


def get_weather_data(config=None):
    print("Getting weather data from yr.no...")
    if config is None:
        config = read_config()
    url = ("https://api.met.no/weatherapi/locationforecast/2.0/complete.json?lat=%s&lon=%s"
           % (config["lat"], config["long"]))
    logger.log("Getting weather data from " + url)

    # Set header
    headers = {"User-Agent": "AEV Weather Station"}
    response = requests.get(url, headers=headers)
    data = response.content.decode("utf-8")
    write_weather_data(data)

    return data


def write_weather_data(weather_data):
    print("Caching weather data...")
    logger.log("Caching weather data")
    with codecs.open("weather.json", encoding="utf-8", mode="w") as weather_json:
        weather_json.write(weather_data)
    weather_json.close()


def get_forecast():
    weather_json = get_weather_data(read_config())
    # Get forecasts
    data = json.loads(weather_json)

    # Get last update
    last_update = data["properties"]["meta"]["updated_at"]

    # Get forecasts for the current time, in 6 hours and in 12 hours
    weather_data_now = data["properties"]["timeseries"][0]
    weather_data_6 = data["properties"]["timeseries"][6]
    weather_data_12 = data["properties"]["timeseries"][12]

    return {
        "weather_now": extract_weather_data(weather_data_now),
        "weather_6": extract_weather_data(weather_data_6),
        "weather_12": extract_weather_data(weather_data_12),
        "last_update": last_update
    }


def extract_weather_data(data):
    time = to_datetime(data["time"])
    return {
        "time": str(time.hour) + ":00",
        "icon": data["data"]["next_1_hours"]["summary"]["symbol_code"],
        "wind_speed": data["data"]["instant"]["details"]["wind_speed"],
        "wind_direction": get_wind_direction(data["data"]["instant"]["details"]["wind_from_direction"]),
        "temperature": data["data"]["instant"]["details"]["air_temperature"],
        "pressure": data["data"]["instant"]["details"]["air_pressure_at_sea_level"]
    }


def get_wind_direction(angle):  # angle is measured in degrees
    if angle < 30.0 or angle > 330.0:
        return u"nord"
    elif angle < 60.0:
        return u"øst-nordøst"
    elif angle < 120.0:
        return u"øst"
    elif angle < 150.0:
        return u"øst-sørøst"
    elif angle < 210.0:
        return u"sør"
    elif angle < 240.0:
        return u"vest-sørvest"
    elif angle < 300.0:
        return u"vest"
    else:
        return u"vest-nordvest"


def get_credits():
    return [u"Værvarsel fra Yr, ", u"levert av NRK og Meteorologisk institutt"]


def to_datetime(timestamp):
    date, time = timestamp.split("T")
    year, month, day = date.split("-")
    hour, minute, second = time.split(":")

    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second[:2]))
