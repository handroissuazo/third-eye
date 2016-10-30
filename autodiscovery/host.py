from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname
import pbuffer

# ---------------- CONSTANTS ------------------
HOST_MAINTENANCE_PORT = 40000
CLIENT_MAINTENANCE_PORT = 50000
MAGIC = "suaZ01713" #to make sure we don't confuse or get confused by other programs

# ---------------- GLOBALS ------------------
PROCESS_BUFFER = {}


def discover_nodes(process_buff):
    global PROCESS_BUFFER
    PROCESS_BUFFER = process_buff

    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', HOST_MAINTENANCE_PORT))

    while 1:
        data, addr = s.recvfrom(1024) #wait for a packet
        strData = data.decode('utf-8')
        if strData.startswith(MAGIC):
            strIP = data[len(MAGIC):]
            print("got service announcement from {}".format(strIP))
            send_client_ip_to_main(strIP)
            data = ""


def send_client_ip_to_main(strIP):
    PROCESS_BUFFER.enqueue("hostModule", "new_node", strIP)


def send_host_info_to_client(clientIP, host_info):
    s = socket(AF_INET, SOCK_DGRAM)  # create UDP socket
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)  # this is a broadcast socket

    strInfo = MAGIC + host_info
    encodedInfo = strInfo.encode('utf-8')

    s.sendto(encodedInfo, (clientIP, CLIENT_MAINTENANCE_PORT))
    s.close()
    print("sent video port announcement")