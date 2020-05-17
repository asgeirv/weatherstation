from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import configparser
import os
import traceback

def write_place(place):
    place['country'] = 'Norge'
    config = configparser.ConfigParser()
    config['loc'] = place
    with open('../../weather.conf', 'w') as config_file:
        config.write(config_file)
    os.system('cd /home/pi/weatherstation && python3 weather_station.py')

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            parsed_url = urlparse(self.path)
            if parsed_url.path == '/sted':
                self.handle_get_place(parsed_url)
            else:
                self.send_response(404, 'Route not found')
                self.end_headers()
                return
        except:
            self.send_error(500, 'Internal server error')
            self.end_headers()
            traceback.print_exc()

    def handle_get_place(self, parsed_url):
        params = parse_qs(parsed_url.query)

        try:
            place = {
                'region': padrams['region'][0],
                'municipality': params['kommune'][0],
                'location': params['lokasjon'][0]
            }
        except KeyError as e:
            self.send_error(400, f'{e} must be supplied')
            self.end_headers()
            return

        write_place(place)

        self.send_response(200)
        self.end_headers()

server_address = ('', 8000)
httpd = HTTPServer(server_address, Handler)
httpd.serve_forever()
