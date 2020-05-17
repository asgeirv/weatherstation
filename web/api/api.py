from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import configparser
import os
import traceback
import yr

def write_place(place):
    config = configparser.ConfigParser()
    config['loc'] = place
    with open('../../weather.conf', 'w') as config_file:
        config.write(config_file)
    os.system('cd /home/pi/weatherstation && python3 weather_station.py')

def verify_place(place):
    try:
        yr.get_forecast((place['country'], place['region'], place['municipality'], place['location']))
        return True
    except:
        traceback.print_exc()
        return False

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
                'country': 'Norge',
                'region': params['region'][0],
                'municipality': params['kommune'][0],
                'location': params['lokasjon'][0]
            }
        except KeyError as e:
            self.send_error(400, f'{e} must be supplied')
            self.end_headers()
            return

        if not verify_place(place):
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(bytes('Invalid place or something idk', 'utf-8'))
            return

        write_place(place)

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        for credits in yr.get_credits():
            self.wfile.write(bytes(credits + '\n', 'utf-8'))

server_address = ('', 8000)
httpd = HTTPServer(server_address, Handler)
httpd.serve_forever()
