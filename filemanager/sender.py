from socket import socket, AF_INET
import sys
from autodiscovery import comms

def send_video(server_address,server_port):
    # Create a TCP/IP socket
    sock = socket.socket(AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (server_address, server_port)
    print >>sys.stderr, 'connecting to %s port %s' % server_address
    sock.connect(server_address)

    try:
        f = open('SampleVideo_1280x720_50mb.mp4', 'rb') #open in binary
        l = f.read(1024)
        packet = l
        while (l):
            l = f.read(1024)
            packet += l

        # Send data
        message = 'This is the message.'
        print >>sys.stderr, 'sending "%s"' % message
        comms.send_msg(sock, packet)

        print >>sys.stderr, 'Recieved "%s"' % comms.recv_msg(sock)

    finally:
        print >>sys.stderr, 'closing socket'
        f.close()
        sock.close()


