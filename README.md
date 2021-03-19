# Weather Station
Gets weather data from www.yr.no and displays it on a Waveshare 7.5 inch E-ink screen (https://www.waveshare.com/wiki/7.5inch_e-Paper_HAT).

### Notes
Make a copy of `weather-base-config.conf` and rename the copy to `weather.conf`. Edit this file to configure. 
Connect via port 8000 for web interface (WIP)

Configure cron (`crontab -e`) to run once every hour and on reboot:

`@reboot PYTHONPATH=/home/pi/weatherstation/include:$PYTHONPATH bash -c "cd /home/pi/weatherstation && python3 weather_station.py" &`

`@hourly PYTHONPATH=/home/pi/weatherstation/include:$PYTHONPATH bash -c "cd /home/pi/weatherstation && python3 weather_station.py" &`

The SSL connection to yr.no requires an RNG with sufficient entropy, when running headless the inbuilt Raspberry Pi one is not good enough so install `haveged` (http://issihosts.com/haveged/):

`sudo apt install haveged`

Also make sure that `var/log/weatherstation_log.txt` exists and is writable.
