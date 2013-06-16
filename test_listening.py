import socket
import sys
import time

server_address = ('localhost', 10000)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

while True:
    print sock.recv(1024)
    time.sleep(2)
sock.close()
