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

    return {
        "lat": config_parser.get("loc", "lat"),
        "long": config_parser.get("loc", "long"),
        "future_interval": config_parser.get("future", "interval")
    }


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
    config = read_config()
    weather_json = get_weather_data(config)

    first_future_time = 6
    future_interval = int(config["future_interval"])

    # Get forecasts
    data = json.loads(weather_json)

    # Get last update
    last_update = data["properties"]["meta"]["updated_at"]

    # Get forecasts
    weather_data_now = data["properties"]["timeseries"][0]
    weather_data_future1 = data["properties"]["timeseries"][first_future_time]
    weather_data_future2 = data["properties"]["timeseries"][first_future_time + future_interval]
    weather_data_future3 = data["properties"]["timeseries"][first_future_time + (future_interval * 2)]
    weather_data_future4 = data["properties"]["timeseries"][first_future_time + (future_interval * 3)]
    weather_data_future5 = data["properties"]["timeseries"][first_future_time + (future_interval * 4)]

    return {
        "weather_now": extract_weather_data(weather_data_now),
        "weather_future": [
            extract_weather_data(weather_data_future1),
            extract_weather_data(weather_data_future2),
            extract_weather_data(weather_data_future3),
            extract_weather_data(weather_data_future4),
            extract_weather_data(weather_data_future5)
        ],
        "last_update": last_update
    }


def extract_weather_data(data):
    time = to_datetime(data["time"])
    return {
        "time": str(time.hour).zfill(2) + ":00",
        "icon": data["data"]["next_1_hours"]["summary"]["symbol_code"],
        "wind_speed": data["data"]["instant"]["details"]["wind_speed"],
        "wind_speed_of_gust": data["data"]["instant"]["details"]["wind_speed_of_gust"],
        "wind_direction": get_wind_direction(data["data"]["instant"]["details"]["wind_from_direction"]),
        "temperature": data["data"]["instant"]["details"]["air_temperature"],
        "pressure": data["data"]["instant"]["details"]["air_pressure_at_sea_level"]
    }


def get_wind_direction(angle):  # angle is measured in degrees
    if angle < 11.25 or angle > 348.75:
        return u"nord"
    elif angle < 33.75:
        return u"nord-nordøst"
    elif angle < 56.25:
        return u"nordøst"
    elif angle < 78.75:
        return u"øst-nordøst"
    elif angle < 101.25:
        return u"øst"
    elif angle < 123.75:
        return u"øst-sørøst"
    elif angle < 146.25:
        return u"sørøst"
    elif angle < 168.75:
        return u"sør-sørøst"
    elif angle < 191.25:
        return u"sør"
    elif angle < 213.75:
        return u"sør-sørvest"
    elif angle < 236.25:
        return u"sørvest"
    elif angle < 258.75:
        return u"vest-sørvest"
    elif angle < 281.25:
        return u"vest"
    elif angle < 303.25:
        return u"vest-nordvest"
    elif angle < 326.25:
        return u"nordvest"
    else:
        return u"nord-nordvest"


def get_credits():
    return [u"Værvarsel fra Yr, ", u"levert av NRK og Meteorologisk institutt"]


def to_datetime(timestamp):
    date, time = timestamp.split("T")
    year, month, day = date.split("-")
    hour, minute, second = time.split(":")

    return datetime(int(year), int(month), int(day), int(hour), int(minute), int(second[:2]))
