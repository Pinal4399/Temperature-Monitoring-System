It is my Msc in Advanced Computer Science project which I built for my Smart System Module.

The aim of this project is to monitor the temperature and humidity to protect important data on the 
server in the server room by using a BME280 sensor and raspberry pi respectively. 

Objectives 
● To implement the transmission of the data to the server in real-time mode  
  through OpenStack. 
● To help avoid heat build-up in a server room like industries or student  IT institutions.  
● To carry out server rooms from unexpected changes in rooms heating when power failure.

Hardware Connections
Raspberry pi is a small-sized computer and can be utilized as a router, media center, web server, and other things. The Raspberry Pi uses a Linux-based operating system to operate the device. Raspberry runs using
python code.  The Raspberry uses BME 280 sensor to determine the room's temperature and humidity. BME280 sensor and LED 5*5 Matrix connect to raspberry 400 with Breakout Garden through the ribbon cable. The raspberry 
pi will activate the web server service after reading the raspberry and send the temperature and humidity data over a local wireless network (a private network). If the temperature is greater than 22  then the server 
light on the LED 5*5 Matrix and send data to the client.

OpenStack Networking:
In OpenStack, create a network, router, interface, security group and add security rules like ingress ICMP and TCP. Also, add new ssh key pair and launch the instance.

Open terminal type  command: 
sudo apt install net-tools 
sudo route add -net 192.68.0.0/24 gw 192.168.251.165 dev wlan0 
Run server and client code file for monitoring temperature data.


