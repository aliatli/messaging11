# import all the required modules
import socket
import threading

# import all functions /
# everything from chat.py file
# from server import *
from gui import GUI

PORT = 5050
SERVER = "127.0.0.1"
ADDRESS = (SERVER, PORT)
FORMAT = "utf-8"

# Create a new client socket
# and connect to the server
client = socket.socket(socket.AF_INET,
                       socket.SOCK_STREAM)
client.connect(ADDRESS)
print(client)
# create a GUI class object
g = GUI("client", client, client.getsockname())
