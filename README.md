# [Demo Video](https://youtu.be/kd3CyjUY80Q)
# Deployment
## Starting TCP server
```
python3 server.py
```
## Starting POX controller 
```
sudo ./pox/pox.py captive_portal
```
## Starting Mininet 
```
sudo python3 setUpMininet.py
```
### Starting DNS Server in Mininet
```
xterm host
python3 dns_server.py
```
### Starting WEB Server in Mininet
```
xterm host
python3 web_server.py
```
## Testing
```
h1 firefox
```
```
h2 firefox
```
