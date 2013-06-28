import socket
import pyaudio
import time


chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 15000
timer = 0

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=chunk
)


messages = [
    'TALK John: REQUEST',
]
server_address = ('localhost', 9300)
# Create a TCP/IP socket
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect(server_address)
tcp_sock.send('CONNECT: "Will" "William Wilkinson" 1.0.0\r\n')
for message in messages:
    tcp_sock.send(message)
session_key = 0
found = False
while True:
    rawdata = tcp_sock.recv(1024)
    for data in rawdata.split("\r\n"):
        print data
        if data.startswith("TALK"):
            found = True
            session_key = data.split(":")[0].split()[2]
            break
    if found:
        break
tcp_sock.close()

# server_address = ('192.81.221.23', 10000)
server_address = ('localhost', 9301)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.sendto("TALKSESSION: %s \r\n" % session_key, server_address)

time.sleep(0.5)
sock.sendto("blaaaaaaaaaaaaasdmalskdmlaskmdlkasd\r\n", server_address)
time.sleep(0.5)
sock.sendto("asdasdasdafafafsdfsdfsbxcbxcbxcafaf\r\n", server_address)
time.sleep(0.5)
sock.sendto("dhdfhdfhdfhdfsaadadadaddahdfhdfhdfh\r\n", server_address)
time.sleep(0.5)
sock.sendto("rtyrtyrtyrtyrtmnxururturturturturtu\r\n", server_address)

sock.close()

