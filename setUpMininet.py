from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Intf
import configparser

config = configparser.ConfigParser()
config.read('config.ini')
captive_portal_ip = config['DEFAULT']['captive_portal_ip']
captive_portal_mac = config['DEFAULT']['captive_portal_mac']
internet_ip = config['DEFAULT']['internet_ip']
internet_mac = config['DEFAULT']['internet_mac']

def configure_network(host):
    host.cmd('sudo systemctl disable --now systemd-resolved.service')
    host.cmd(f'echo -e "nameserver 127.0.0.53\nnameserver {captive_portal_ip}\nnameserver 8.8.8.8" > /etc/resolv.conf')
    host.cmd(f'sudo ip route add 0.0.0.0/0 via {internet_ip} metric 100')
    host.cmd(f'sudo ip route add 0.0.0.0/0 via {captive_portal_ip} metric 200')
    host.cmd('export XAUTHORITY=/root/.Xauthority')

def customTree():
    "Create a network and add NAT to provide Internet access."

    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    info('*** Adding host\n')
    host = net.addHost('host', mac=captive_portal_mac, ip=captive_portal_ip)

    info('*** Adding internet connectivity\n')
    internet = net.addNAT(name='internet', mac=internet_mac)
    internet.configDefault()

    info('*** Adding users\n')
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')

    info('*** Creating links\n')
    net.addLink(s1, host)
    net.addLink(s1, internet)
    net.addLink(s1, s2)
    net.addLink(s2, h1)
    net.addLink(s2, h2)

    info('*** Starting network\n')
    net.start()

    info('*** Configure NAT setting\n')
    internet.cmd(f'ifconfig internet-eth0 {internet_ip} netmask 255.0.0.0')

    info('*** Configure user network\n')
    configure_network(h1)
    configure_network(h2)

    # info('*** Start host service\n')
    # host.cmd('python3 dns_server.py &')
    # host.cmd('python3 web_server.py &')

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTree()
