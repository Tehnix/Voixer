import socket
import sys
import time

server_address = ('localhost', 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

sock.send('CONNECT: "Johnsie" "John Wilkens" 1.0.0')

while True:
    rawdata = sock.recv(1024)
    if rawdata:
        for data in rawdata.split("\r\n"):
            print data
            if data.startswith("PING"):
                ping_num = data.split(":")[1].strip()
                pong = "PONG: %s\r\n" % ping_num
                sock.send(pong)
                print ">>>  %s" % pong
            if data.startswith("MSG"):
                sock.send("JOIN: #Hej man\r\n")
                sock.send("MSG #lobby: Johnsie just send this!\r\n")
    else:
        break
    time.sleep(2)
sock.close()
