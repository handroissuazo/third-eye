import socket
import sys
from autodiscovery import comms


def receive_on_port(n_port):
    dCameras = {}

    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind the socket to the port
    server_address = ('localhost', n_port)
    print >>sys.stderr, 'starting up on %s port %s' % server_address
    sock.bind(server_address)

    # Listen for incoming connections
    sock.listen(1)

    while True:
        # Wait for a connection
        print >>sys.stderr, 'waiting for a connection'
        connection, client_address = sock.accept()

        try:
            print >>sys.stderr, 'connection from', client_address

            data = comms.recv_msg(connection)
            if data:
                print >>sys.stderr, 'sending data back to the client'
                comms.send_msg(connection, 'Thanks! Bye!')

            f = open('receive.mp4', 'wb')
            f.write(data)
            f.close()
        finally:
            # Clean up the connection
            connection.close()


