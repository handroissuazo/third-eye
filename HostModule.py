import socket
import time

#from multiprocessing import Process
from threading import Thread
from autodiscovery import host
from pbuffer import pbuffer

# ---------------- CONSTANTS ------------------
MAGIC = "suaZ01713" #to make sure we don't confuse or get confused by other programs

# ----------------- GLOBALS ------------------
CLIENT_NODES = []     # This contains the ports that are currently in use to send/receive data
PROCESS_BUFFER = pbuffer.PBuffer()

# ---------------- SERVER PROGRAM ----------------
def create_new_node(nodeIP):
    currentPort = 0
    if not CLIENT_NODES:
        CLIENT_NODES.append({"node_ip": nodeIP, "node_port": 10001})
    else:
        CLIENT_NODES.append({"node_ip": nodeIP, "node_port": CLIENT_NODES[-1]["node_port"] + 1}) # Add 1 to last used port to get next available port

    return CLIENT_NODES[-1]

def respond_to_new_node_with_host_info(client_node):
    host_ip = socket.gethostbyname(socket.gethostname())
    host_info = host_ip + ":" + str(client_node["node_port"])
    host.send_host_info_to_client(client_node["node_ip"], host_info)


def setup_directory():
    # Check if save directory exists
    # Create dir if not
    print("Directory Setup")


def start_server(pBuff):
    while 1:
        packet = pBuff.dequeue()
        if packet:
            if packet['destination'] is "hostModule":
                pBuff.thanks()

                if packet["action"] is "new_node":
                    new_node = create_new_node(packet["data"].decode("utf-8"))
                    respond_to_new_node_with_host_info(new_node)
            else:
                pBuff.no_thanks()
        time.sleep(1)


if __name__ == '__main__':
    ##---  start first process and send dictionary
    p = Thread(target=host.discover_nodes, args=(PROCESS_BUFFER,))
    s = Thread(target=start_server, args=(PROCESS_BUFFER,))
    s.start()
    p.start()

