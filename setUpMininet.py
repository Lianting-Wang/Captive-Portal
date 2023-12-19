from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import Intf

def customTree():
    "Create a network and add NAT to provide Internet access."

    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    info('*** Adding controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    info('*** Adding host\n')
    host = net.addHost('host', mac='00:00:00:00:00:01', ip='10.0.0.2')

    info('*** Adding NAT connectivity\n')
    internet = net.addNAT(name='internet', mac='00:00:00:00:00:02')
    internet.configDefault()

    info('*** Adding user\n')
    h1 = net.addHost('h1', defaultRoute='via 10.0.0.2')
    h2 = net.addHost('h2', defaultRoute='via 10.0.0.2')

    info('*** Creating links\n')
    net.addLink(s1, host)
    net.addLink(s1, internet)
    net.addLink(s1, s2)
    net.addLink(s2, h1)
    net.addLink(s2, h2)

    # info('*** DNS\n')
    # h1.cmd('cp -f resolv.conf /etc/')

    info('*** Starting network\n')
    net.start()

    # info('*** DNS\n')
    # h1.cmd('echo "nameserver 8.8.8.8" > /etc/resolv.conf')
    # print(h1.cmd('cat /etc/resolv.conf'))
    # print(h1.cmd('cat /etc/NetworkManager/NetworkManager.conf'))

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTree()
