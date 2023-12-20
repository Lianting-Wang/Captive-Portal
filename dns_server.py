from scapy.all import *

def dns_responder(packet):
    if packet.haslayer(DNSQR): # DNS question record
        ip = '10.0.0.1' # Assumed response IP address
        queried_host = packet[DNSQR].qname.decode('utf-8')
        if queried_host == 'captive-portal.wlt.life.':
            ip = '10.0.0.1' # Response IP address for a specific domain name
        dns_response = IP(dst=packet[IP].src, src=packet[IP].dst) /\
                       UDP(dport=packet[UDP].sport, sport=packet[UDP].dport) /\
                       DNS(id=packet[DNS].id, qr=1, aa=1, qd=packet[DNS].qd,\
                           an=DNSRR(rrname=packet[DNS].qd.qname, ttl=10, rdata=ip))
        send(dns_response)
        print(f"Sent DNS response with IP {ip} for query {queried_host}")

# Setting up a sniffer to capture DNS requests
sniff(filter="udp and port 53", prn=dns_responder, store=0, promisc=True)
