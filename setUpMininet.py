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

    router='10.0.0.1'

    info('*** Adding host\n')
    host = net.addHost('host', mac='00:00:00:00:00:01', ip=router)

    info('*** Adding NAT connectivity\n')
    internet = net.addNAT(name='internet', mac='00:00:00:00:00:02')
    internet.configDefault()

    info('*** Adding users\n')
    h1 = net.addHost('h1', defaultRoute=f'via {router}')
    h2 = net.addHost('h2', defaultRoute=f'via {router}')

    info('*** Creating links\n')
    net.addLink(s1, host)
    net.addLink(s1, internet)
    net.addLink(s1, s2)
    net.addLink(s2, h1)
    net.addLink(s2, h2)

    info('*** Starting network\n')
    net.start()

    info('*** Configure DNS for users\n')
    h1.cmd('sudo systemctl disable --now systemd-resolved.service')
    h2.cmd('sudo systemctl disable --now systemd-resolved.service')
    h1.cmd(f'echo -e "nameserver 127.0.0.53\nnameserver {router}\nnameserver 8.8.8.8" > /etc/resolv.conf')
    h2.cmd(f'echo -e "nameserver 127.0.0.53\nnameserver {router}\nnameserver 8.8.8.8" > /etc/resolv.conf')

    info('*** Fixed internet IP\n')
    internet.cmd(f'ifconfig internet-eth0 {router} netmask 255.0.0.0')

    info('*** Running CLI\n')
    CLI(net)

    info('*** Stopping network\n')
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    customTree()
