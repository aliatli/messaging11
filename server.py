# import socket library
import socket

# import threading library
import threading

# Choose a port that is free
from gui import GUI

PORT = 5050

# An IPv4 address is obtained
# for the server.
SERVER = '127.0.0.1'  # socket.gethostbyname(socket.gethostname())

# Address is stored as a tuple
ADDRESS = (SERVER, PORT)

# the format in which encoding
# and decoding will occur
FORMAT = "utf-8"

# Create a new socket for
# the server
server = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)

# bind the address of the
# server to the socket
server.bind(ADDRESS)


# function to start the connection
def start_chat():
    print("server is working on " + SERVER)

    # listening for connections
    server.listen()

    while True:
        # accept connections and the address bound to it
        conn, addr = server.accept()

        # Start the handling thread
        thread = threading.Thread(target=handle,
                                  args=(conn, addr))
        thread.start()


def handle(conn, addr):
    g = GUI("server", conn, conn.getsockname())


# call the method to
# begin the communication
start_chat()
