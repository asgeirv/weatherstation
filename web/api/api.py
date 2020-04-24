from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import configparser
import os

def write_place(place):
    place['country'] = 'Norge'
    config = configparser.ConfigParser()
    config['loc'] = place
    with open('../../weather.conf', 'w') as config_file:
        config.write(config_file)
    os.system("python3 /home/pi/weatherstation/weather_station.py")

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        parsed_url = urlparse(self.path)
        if parsed_url.path == '/sted':
            self.handle_get_place(parsed_url)
        else:
            self.send_response(404)
            self.end_headers()
            return

    def handle_get_place(self, parsed_url):
        params = parse_qs(parsed_url.query)
        place = {
            'region': params['region'][0],
            'municipality': params['kommune'][0],
            'location': params['lokasjon'][0]
        }

        write_place(place)

        self.send_response(200)
        self.end_headers()

server_address = ('', 8000)
httpd = HTTPServer(server_address, Handler)
httpd.serve_forever()
