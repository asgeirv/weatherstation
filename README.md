# Weather Station
Gets weather data from www.yr.no and displays it on a Waveshare 5.65 7-color inch E-ink screen (https://www.waveshare.com/wiki/5.65inch_e-Paper_Module_(F)).

### Notes
Make a copy of `weather-base-config.conf` and rename the copy to `weather.conf`. Edit this file to configure. 
Connect via port 8000 for web interface (WIP)

The SSL connection to yr.no requires an RNG with sufficient entropy, when running headless the inbuilt Raspberry Pi one is not good enough so install `haveged` (http://issihosts.com/haveged/):

`sudo apt install haveged`

The application uses the Lato font:

`sudo apt install fonts-lato`

Make sure dependencies for GPIO are installed:

```
pip3 install spidev
pip3 install RPi.GPIO
```

Install PIL

`pip3 install pillow`

Install dependencies for pillow

```
sudo apt install libopenjp2-7 -y
sudo apt install libtiff5 -y
```

Enable SPI: `sudo raspi-config` -> Interface Options -> SPI

Make sure that `var/log/weatherstation_log.txt` exists and is writable.

Configure cron (`crontab -e`) to run once every hour and on reboot:

`@reboot PYTHONPATH=/home/pi/weatherstation/include:$PYTHONPATH bash -c "cd /home/pi/weatherstation && python3 weather_station.py" &`

`@hourly PYTHONPATH=/home/pi/weatherstation/include:$PYTHONPATH bash -c "cd /home/pi/weatherstation && python3 weather_station.py" &`
