import socket
import sys

messages = [
    'MSG #Lobby: Hey All!\r\n',
    'MSG Johnsie: Hey Johnsie!\r\n',
    'MSG John: Hey John!\r\n',
    'TALK John: REQUEST',
    #'Talk John: End',
    #'JOIN: #TurboRoom\r\n',
    #'TALK Michael: Deny',
    #'TALK Michael: Accept',
    'DISCONNECT\r\n'
]
server_address = ('localhost', 10000)

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)
sock.send('CONNECT: "Will" "William Wilkinson" 1.0.0\r\n')

for message in messages:
    print >>sys.stderr, 'sending "%s"' % (message)
    sock.send(message)
sock.close()
