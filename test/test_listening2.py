import socket
import sys
import time

server_address = ('localhost', 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

sock.send('CONNECT: "Johnsie" "John Wilkens" 1.0.0')

while True:
    data = sock.recv(1024)
    if data:
        print data
        if data.startswith("PING"):
            ping_num = data.split(":")[1].strip()
            pong = "PONG: %s" % ping_num
            sock.send(pong)
            print ">>>  %s" % pong
        if data.startswith("MSG"):
            sock.send("JOIN: #Hej man")
    else:
        break
    time.sleep(2)
sock.close()
