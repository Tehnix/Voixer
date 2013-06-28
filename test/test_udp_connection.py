import socket
import pyaudio


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

server_address = ('localhost', 10000)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.connect(server_address)

sock.send("TALKSESSION: %s \r\n" % 631720830760049)



sock.close()

