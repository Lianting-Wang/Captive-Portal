from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def customTree():
    "Create a network without using the built-in tree topology."

    net = Mininet(controller=RemoteController, switch=OVSSwitch)

    info('*** Adding remote controller\n')
    net.addController('c0')

    info('*** Adding switches\n')
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')
    s3 = net.addSwitch('s3')

    info('*** Adding hosts\n')
    h1 = net.addHost('h1', mac='00:00:00:00:00:01')
    h2 = net.addHost('h2')
    h3 = net.addHost('h3')
    h4 = net.addHost('h4')

    info('*** Creating links\n')
    net.addLink(s1, s2)
    net.addLink(s1, s3)
    net.addLink(s2, h1)
    net.addLink(s2, h2)
    net.addLink(s3, h3)
    net.addLink(s3, h4)

    info('*** Starting network\n')
    net.start()
    
    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTree()
