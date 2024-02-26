from scapy.all import *
import socket

def forward_dns_query(data, server='8.8.8.8', port=53):
    """Forward DNS query to a specified DNS server and return the response."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(2)  # Set a timeout
        sock.sendto(data, (server, port))
        try:
            response, _ = sock.recvfrom(1024)  # Adjusting size for larger responses
        except socket.timeout:
            return None
    return response

def dns_interceptor(packet):
    """Intercept DNS requests and forward them to a specified DNS server."""
    # Only intercept DNS queries from the client
    if packet.haslayer(DNSQR) and packet[IP].src != '10.0.0.1' and packet[IP].src != '8.8.8.8':
        print(f"Received DNS query for {packet[DNSQR].qname} from {packet[IP].src} to {packet[IP].dst}")
        original_data = bytes(packet[UDP].payload)
        response_data = forward_dns_query(original_data)
        
        if response_data:
            response_packet = DNS(response_data)
            # Send the response back to the client
            spoofed_pkt = IP(dst=packet[IP].src, src=packet[IP].dst) /\
                          UDP(dport=packet[UDP].sport, sport=packet[UDP].dport) /\
                          DNS(id=packet[DNS].id, qr=1, aa=packet[DNS].aa, qd=packet[DNS].qd,
                              an=response_packet.an, ns=response_packet.ns, ar=response_packet.ar)
            send(spoofed_pkt, verbose=0)
            print(f"Forwarded DNS response to {packet[IP].src}")
        else:
            print("Failed to receive DNS response from 10.0.0.2")

# Start the DNS interceptor
sniff(filter="udp port 53", prn=dns_interceptor)
