from socket import socket, AF_INET, SOCK_DGRAM, SOL_SOCKET, SO_BROADCAST, gethostbyname, gethostname

# ---------------- CONSTANTS ------------------
CLIENT_MAINTENANCE_PORT = 50000
SERVER_MAINT_PORT = 40000
MAGIC = "suaZ01713" # to make sure we don't confuse or get confused by other programs


# ---------------- GLOBALS -----------------------
CURRENT_STATE = "STARTUP"


# ----------------- FUNCTIONS -------------------
def start_self_discovery():
    # This function returns host IP and receiving port for future communication in format: ['<IP>':'<PORT>']
    host_info = announce_presence()
    return host_info.split(':')


def announce_presence():
    global CURRENT_STATE
    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.bind(('', 0))
    s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1) #this is a broadcast socket
    myIp = gethostbyname(gethostname())  #get our IP. Be careful if you have multiple network interfaces or IPs # alternative:

    host_info = ""

    # announce_presence through UDP.
    while CURRENT_STATE is "STARTUP":
        data = MAGIC+myIp
        byteData = data.encode('utf-8')

        s.sendto(byteData, ('<broadcast>', SERVER_MAINT_PORT))
        print("sent service announcement")
        host_info = wait_for_discovery_from_server(2)

    return host_info


def wait_for_discovery_from_server(n_timeout):
    global CURRENT_STATE
    s = socket(AF_INET, SOCK_DGRAM) #create UDP socket
    s.settimeout(n_timeout)
    s.bind(('', CLIENT_MAINTENANCE_PORT))

    host_ip_and_port = ""

    try:
        data, addr = s.recvfrom(1024) #wait for a packet
        strData = data.decode("utf-8")
        if strData.startswith(MAGIC):
            CURRENT_STATE = "STARTED"
            host_ip_and_port = data[len(MAGIC):].decode("utf-8")
            print("was discovered by:", host_ip_and_port)

    except:
        print("T/O: Waiting for discovery")

    s.close()
    return host_ip_and_port

