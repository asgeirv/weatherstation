from datetime import datetime

def log(msg):
    with open("/var/log/weatherstation_log.txt", "a") as log_file:
        log_file.write("[%s]: %s\n" % (datetime.now(), msg))
