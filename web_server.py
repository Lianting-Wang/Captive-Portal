import ssl
import json
import threading
import socketserver
from urllib.parse import parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler
from scapy.all import ARP, Ether, srp
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
ssl_enable = config['DEFAULT']['ssl_enable']
keyfile = config['DEFAULT']['keyfile']
certfile = config['DEFAULT']['certfile']
captive_portal_host = config['DEFAULT']['captive_portal_host']

protocol = 'http'
if (ssl_enable == 'True'):
    protocol = 'https'

class RedirectHandler(SimpleHTTPRequestHandler):
    def get_mac(self, ip):
        """ Use an ARP request to obtain the MAC address of a specified IP """
        # Constructing an Ethernet broadcast frame and ARP request
        arp_request = ARP(pdst=ip)
        broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request

        # Send a request and get a response
        answered, _ = srp(arp_request_broadcast, timeout=2, verbose=False)

        # Extract MAC address from response
        return answered[0][1].hwsrc if answered else "Unknown"
    
    def redirect_handler(self, redirect_domain, host):
        self.send_response(302)
        self.send_header('Location', f'{protocol}://{redirect_domain}/?original_host={host}')
        self.end_headers()
    
    def request_handler(self):
        path = self.path.split('?', 1)[0]

        if path == '/':
            path = '/index.html'
        elif '.' not in path:
            path += '.html'

        if path.endswith(".html"):
            mimetype = 'text/html'
        elif path.endswith(".css"):
            mimetype = 'text/css'
        elif path.endswith(".js"):
            mimetype = 'application/javascript'
        else:
            mimetype = 'text/plain'

        try:
            with open(f'web/{path[1:]}', 'rb') as file: 
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(file.read())
        except FileNotFoundError:
            self.send_error(404, 'File Not Found: %s' % path)

    def do_GET(self):
        # Check the host header to determine the domain of the request
        host = self.headers.get('Host')

        # Define the target domain for the redirect
        # redirect_domain = 'captive-portal.com'
        redirect_domain = captive_portal_host

        # If the request is for a different domain, redirect to the captive portal
        if host and host != redirect_domain:
            self.redirect_handler(redirect_domain, f'https://{host}{self.path}')
        else:
            # Otherwise, serve the normal content
            self.request_handler()
    
    def do_POST(self):
        # Get the requested IP and MAC address
        request_ip = self.client_address[0]
        mac_address = self.get_mac(request_ip)

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        path = self.path.split('?', 1)[0]

        if path == '/login':
            # Parse JSON data
            try:
                data = json.loads(post_data)
            except json.JSONDecodeError:
                self.send_error(400, 'Invalid JSON')
                return

            # Check credentials
            if data.get('username') == 'test' and data.get('password') == 'pass':
                response = {'success': True}
                with open('macset', 'a') as file:
                    file.write(mac_address)
            else:
                response = {'success': False}

            # Send JSON response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            response = f'404 Not Found: {path}'
            self.wfile.write(response.encode('utf-8'))

def run(port):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RedirectHandler)
    print(f'Starting httpd server on port {port}')
    return httpd

# Starting the HTTP server
def start_http_server():
    httpsd = run(port=80)
    httpsd.serve_forever()

# Starting the HTTPS server
def start_https_server():
    httpsd = run(port=443)
    httpsd.socket = ssl.wrap_socket(httpsd.socket, 
                                    keyfile=keyfile, 
                                    certfile=certfile, 
                                    server_side=True)
    httpsd.serve_forever()

threading.Thread(target=start_http_server).start()
if (ssl_enable == 'True'):
    threading.Thread(target=start_https_server).start()
