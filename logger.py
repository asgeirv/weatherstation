import datetime

def log(msg):
    with open("log.txt", "a") as log_file:
        log_file.write("[%s]: %s\n" % (datetime.now(), msg))
