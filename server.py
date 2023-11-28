import json
import socket
import sys
import threading
from datetime import datetime, timedelta

valid_time = timedelta(days=1)

class MACSet:
    def __init__(self):
        self.approved_macs = {}

    def add_mac(self, mac):
        self.approved_macs[mac] = datetime.now()
        return True

    def remove_mac(self, mac):
        if mac in self.approved_macs:
            del self.approved_macs[mac]
            print(f"Mac {mac} removed.")
            return True
        else:
            print(f"Mac {mac} not found.")
            return False

    def check_mac(self, mac):
        if mac in self.approved_macs:
            print(f"Mac {mac} is approved, added on {self.approved_macs[mac]}. {datetime.now()-self.approved_macs[mac] < valid_time}")
            return True
        else:
            print(f"Mac {mac} is not approved.")
            return False

class Server:
    def __init__(self, MAC='00:00:00:00:00:00', host='127.0.0.1', port=65432):
        self.host = host
        self.port = port
        self.MAC = MAC
        self.MACSet = MACSet()
        self.server_socket = None
        self.lock = threading.Lock()
    
    def handle_client(self, conn, addr):
        print('Connected by', addr)
        try:
            while True:
                data = conn.recv(1024).decode()
                if not data:
                    break
                try:
                    request = json.loads(data)
                    print(f"Received message: {request}")
                    response = self.handle_request(request)
                    conn.sendall(json.dumps(response).encode())
                except json.JSONDecodeError:
                    response = {'error': 'Invalid JSON'}
                    conn.sendall(json.dumps(response).encode())
        finally:
            conn.close()

    def run_server(self):
        """Runs a TCP server that stays open even if the client disconnects."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            self.server_socket = s
            s.bind((self.host, self.port))
            s.listen()
            print(f"Server listening on {self.host}:{self.port}")
            while True:  # Stay open forever
                conn, addr = s.accept()
                client_thread = threading.Thread(target=self.handle_client, args=(conn, addr))
                client_thread.start()
    
    def get_host(self):
        with self.lock:
          return {'result': self.MAC}
    
    def set_host(self, value):
        with self.lock:
          self.MAC = value
          return {'result': True}
    
    def add_mac(self, value):
        with self.lock:
          return {'result': self.MACSet.add_mac(value)}
    
    def check_mac(self, value):
        with self.lock:
          return {'result': self.MACSet.check_mac(value)}

    def handle_request(self, request):
        """Handle incoming requests and return a response."""
        command = request.get('command')
        response = {'error': 'Invalid command'}
        if command == 'getHost':
            response = self.get_host()
        elif command == 'setHost':
            response = self.set_host(request.get('value'))
        elif command == 'add':
            response = self.add_mac(request.get('value'))
        elif command == 'check':
            response = self.check_mac(request.get('value'))
        return response

    def stop_server(self):
        """Stops the TCP server."""
        if self.server_socket:
            self.server_socket.close()

server = Server('00:00:00:00:00:01')
server.run_server()
