import threading
import socket
import time


def log(num, text):
    if num == 1:
        print ">>> SEND: %s" % text
    elif num == 2:
        print "                                --- SEND: %s" % text

def got(num, text):
    if num == 1:
        print ">>> RECV: %s" % text
    elif num == 2:
        print "                                --- RECV: %s" % text


def connection(num, ip, port, tcp_message_pair, udp_messages):
    session_key = None
    # Create a TCP/IP socket
    tcp_addr = (ip, port)
    tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_sock.connect(tcp_addr)
    for expect, msg in tcp_message_pair:
        if expect == "":
            tcp_sock.send(msg)
        else:
            found = False
            while True:
                raw_data = tcp_sock.recv(1024)
                for data in raw_data.split("\r\n"):
                    if data == "":
                        continue
                    got(num, data)
                    # 'MSG John #lobby: Thanks for accepting the call!'
                    if data.startswith("TALK"):
                        if "REQUEST" in data:
                            session_key = data.split(":")[0].split()[2]
                            found = True
                            if num != 1:
                                log(num, "TALK %s: ACCEPT" % session_key)
                                tcp_sock.send("TALK %s: ACCEPT\r\n" % session_key)
                            break
                        elif "ACCEPTED" in data:
                            found = True
                            if num == 1:
                                log(num, 'MSG #lobby: Thanks for accepting the call!')
                                tcp_sock.send("MSG #lobby: Thanks for accepting the call!\r\n")
                            break
                    elif expect in data:
                        log(num, msg)
                        tcp_sock.send(msg + "\r\n")
                        found = True
                        break
                if found:
                    break

    # Create a UDP socket
    udp_addr = (ip, port+1)
    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.sendto("TALKSESSION: %s \r\n" % session_key, udp_addr)
    udp_sock.settimeout(1)
    for msg in udp_messages:
        log(num, msg)
        udp_sock.sendto(msg, udp_addr)
        time.sleep(0.5)

    start = time.time()
    i = 1
    while i < len(udp_messages):
        if (time.time() - start) > 5:
            break
        try:
            recv_data, addr = udp_sock.recvfrom(2048)
        except socket.timeout:
            pass
        if recv_data:
            i = i+1
            got(num, recv_data)

    if num == 1:
        log(num, "TALK %s: END" % session_key)
        tcp_sock.send("TALK %s: END\r\n" % session_key)
    else:
        found_end = False
        while True:
            raw_data = tcp_sock.recv(1024)
            for data in raw_data.split("\r\n"):
                if data.startswith("TALK") and "END" in data:
                    got(num, data)
                    found_end = True
                    break
            if found_end:
                break
    udp_sock.close()
    tcp_sock.send("DISCONNECT\r\n")
    tcp_sock.close()


udp_messages = [
    "blaaaaaaaaaaaaasdmalskdmlaskmdlkasd",
    "asdasdasdafafafsdfsdfsbxcbxcbxcafaf",
    "dhdfhdfhdfhdfsaadadadaddahdfhdfhdfh",
    "rtyrtyrtyrtyrtmnxururturturturturtu"
]

message_pair_1 = [
    ("", 'CONNECT: "Will" "William Wilkinson" 1.0.0'),
    ("USERLIST #lobby:", "MSG #lobby: Sup John :)"),
    ('MSG John #lobby: Hey Will!', 'TALK John: REQUEST'),
    (None, None),
    (None, None)
]

message_pair_2 = [
    ("", 'CONNECT: "John" "William Wilkinson" 1.0.0'),
    ("MSG Will #lobby: Sup John :)", "MSG #lobby: Hey Will!"),
    (None, None)
]

t1 = threading.Thread(
    target=connection,
    args=(1, 'localhost', 10000, message_pair_1, udp_messages)
)
t2 = threading.Thread(
    target=connection,
    args=(2, 'localhost', 10000, message_pair_2, udp_messages)
)
t1.start()
t2.start()
t1.join()
t2.join()