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
        "name1": config_parser.get("loc1", "name"),
        "lat1": config_parser.get("loc1", "lat"),
        "long1": config_parser.get("loc1", "long"),
        "name2": config_parser.get("loc1", "name"),
        "lat2": config_parser.get("loc2", "lat"),
        "long2": config_parser.get("loc2", "long"),
        "future_interval": config_parser.get("future", "interval")
    }


def get_weather_data(config=None):
    print("Getting weather data from yr.no...")
    if config is None:
        config = read_config()
    url1 = ("https://api.met.no/weatherapi/locationforecast/2.0/complete.json?lat=%s&lon=%s"
            % (config["lat1"], config["long1"]))
    url2 = ("https://api.met.no/weatherapi/locationforecast/2.0/complete.json?lat=%s&lon=%s"
            % (config["lat2"], config["long2"]))

    # Set header
    headers = {"User-Agent": "RAV Weather Station"}

    logger.log("Getting weather data from " + url1)
    response1 = requests.get(url1, headers=headers)
    data1 = response1.content.decode("utf-8")
    write_weather_data(data1)

    logger.log("Getting weather data from " + url2)
    response2 = requests.get(url2, headers=headers)
    data2 = response2.content.decode("utf-8")
    write_weather_data(data2)

    return data1, data2


def write_weather_data(weather_data):
    print("Caching weather data...")
    logger.log("Caching weather data")
    with codecs.open("weather.json", encoding="utf-8", mode="w") as weather_json:
        weather_json.write(weather_data)
    weather_json.close()


def get_forecast():
    config = read_config()
    (weather_json1, weather_json2) = get_weather_data(config)

    first_future_time = 0
    future_interval = int(config["future_interval"])

    # Get forecasts
    data1 = json.loads(weather_json1)
    data2 = json.loads(weather_json2)

    # Get last update
    last_update = data1["properties"]["meta"]["updated_at"]

    # Get forecasts
    weather1_data_now = data1["properties"]["timeseries"][0]
    weather1_data_future1 = data1["properties"]["timeseries"][first_future_time]
    weather1_data_future2 = data1["properties"]["timeseries"][first_future_time + future_interval]
    weather1_data_future3 = data1["properties"]["timeseries"][first_future_time + (future_interval * 2)]
    weather1_data_future4 = data1["properties"]["timeseries"][first_future_time + (future_interval * 3)]
    weather1_data_future5 = data1["properties"]["timeseries"][first_future_time + (future_interval * 4)]

    weather2_data_now = data2["properties"]["timeseries"][0]
    weather2_data_future1 = data2["properties"]["timeseries"][first_future_time]
    weather2_data_future2 = data2["properties"]["timeseries"][first_future_time + future_interval]
    weather2_data_future3 = data2["properties"]["timeseries"][first_future_time + (future_interval * 2)]
    weather2_data_future4 = data2["properties"]["timeseries"][first_future_time + (future_interval * 3)]
    weather2_data_future5 = data2["properties"]["timeseries"][first_future_time + (future_interval * 4)]

    return {
        "weather_now": extract_weather_data(weather1_data_now),
        "loc1": config["name1"],
        "weather_future1": [
            extract_weather_data(weather1_data_future1),
            extract_weather_data(weather1_data_future2),
            extract_weather_data(weather1_data_future3),
            extract_weather_data(weather1_data_future4),
            extract_weather_data(weather1_data_future5)
        ],
        "loc2": config["name2"],
        "weather_future2": [
            extract_weather_data(weather2_data_future1),
            extract_weather_data(weather2_data_future2),
            extract_weather_data(weather2_data_future3),
            extract_weather_data(weather2_data_future4),
            extract_weather_data(weather2_data_future5)
        ],
        "last_update": last_update
    }


def extract_weather_data(data):
    time = to_datetime(data["time"])
    return {
        "time": str(time.hour).zfill(2) + ":00",
        "icon": data["data"]["next_1_hours"]["summary"]["symbol_code"],
        "wind_speed": data["data"]["instant"]["details"]["wind_speed"],
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
