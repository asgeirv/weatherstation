def log(msg):
    with open("log.txt") as log_file:
        log_file.write(msg + "\n")
