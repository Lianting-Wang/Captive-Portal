import sys
import json
import socket

config = configparser.ConfigParser()
config.read('config.ini')
TCP_server_ip = config['DEFAULT']['TCP_server_ip']
TCP_server_port = int(config['DEFAULT']['TCP_server_port'])

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

    def close_connection(self):
        """Close the connection to the server."""
        self.connection.close()

if __name__ == '__main__':
    # Check if a command-line argument is provided
    if len(sys.argv) == 2:
        command = sys.argv[1]
        client = TCPClient()
        result = client.send_request({'command': command})
        print(result)
        client.close_connection()
    elif len(sys.argv) == 3:
        command = sys.argv[1]
        value = sys.argv[2]
        client = TCPClient()
        result = client.send_request({'command': command, 'value': value})
        print(result)
        client.close_connection()
    else:
        print("Usage: python3 client.py 'setMAC' 'MAC_ADDRESS'")
