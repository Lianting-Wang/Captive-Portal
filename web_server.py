import ssl
import json
import atexit
import threading
import socketserver
from urllib.parse import parse_qs
from http.server import HTTPServer, SimpleHTTPRequestHandler
from scapy.all import ARP, Ether, srp
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
TCP_server_ip = config['DEFAULT']['internet_ip']
TCP_server_port = int(config['DEFAULT']['TCP_server_port'])
ssl_enable = config['DEFAULT']['ssl_enable']
keyfile = config['DEFAULT']['keyfile']
certfile = config['DEFAULT']['certfile']
captive_portal_host = config['DEFAULT']['captive_portal_host']

httpd = None
httpsd = None

protocol = 'http'
if (ssl_enable == 'True'):
    protocol = 'https'

class TCPClient:
  def __init__(self, host=TCP_server_ip, port=TCP_server_port):
    """Create a TCP client that can send and receive messages from a persistent connection."""
    self.host = host
    self.port = port
    self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.connection.connect((host, port))

  def send_request(self, request):
    """Send a JSON request to the server and return the JSON response."""
    self.connection.sendall(json.dumps(request).encode())
    return json.loads(self.connection.recv(1024).decode())

  def set_valid(self, value):
    """Send valid MAC address to thr server."""
    return self.send_request({'command': 'add', 'value': value})

  def close_connection(self):
    """Close the connection to the server."""
    self.connection.close()

# Initialize TCPClient instances globally
global_tcp_client = TCPClient()

# Close the TCP connection when the program exits
def close_tcp_client():
    global_tcp_client.close_connection()

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
            response = {'success': False}
            if data.get('username') == 'test' and data.get('password') == 'pass':
                try:
                    data = global_tcp_client.set_valid(mac_address)
                    if data['result']:
                        response = {'success': True}
                    else:
                        response = {'success': False, 'error': 'MAC address not added correctly'}
                except Exception as e:
                    response = {'success': False, 'error': str(e)}

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
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, RedirectHandler)
    print(f'Starting httpd server on port {port}')
    return httpd

# Starting the HTTP server
def start_http_server():
    global httpd
    httpd = run(port=80)
    httpd.serve_forever()

# Starting the HTTPS server
def start_https_server():
    global httpsd
    httpsd = run(port=443)
    httpsd.socket = ssl.wrap_socket(httpsd.socket, 
                                    keyfile=keyfile, 
                                    certfile=certfile, 
                                    server_side=True)
    httpsd.serve_forever()

# Close the HTTP and HTTPS servers
def close_servers():
    print("Closing HTTP and HTTPS servers...")
    if httpd:
        httpd.shutdown()
        httpd.server_close()
    if httpsd:
        httpsd.shutdown()
        httpsd.server_close()

# Register the close_servers function to be called when the program exits
atexit.register(close_servers)
atexit.register(close_tcp_client)

threading.Thread(target=start_http_server).start()
if (ssl_enable == 'True'):
    threading.Thread(target=start_https_server).start()
