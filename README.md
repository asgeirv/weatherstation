# Weather Station
Gets weather data from www.yr.no and displays it on an E-ink screen.

### Notes
Make a copy of `weather-base-config.conf` and rename the copy to `weather.conf`
Connect via port 8000

Configure cron (`crontab -e`) to run the script once every hour and on reboot:
`@reboot PYTHONPATH=/home/pi/weatherstation/include:$PYTHONPATH bash -c "cd /home/pi/weatherstation && python3 weather_station.py" &
@hourly PYTHONPATH=/home/pi/weatherstation/include:$PYTHONPATH bash -c "cd /home/pi/weatherstation && python3 weather_station.py" &
`

Also make sure that `var/log/.txt` exists and is writable.
