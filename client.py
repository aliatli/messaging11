import socket
import sys

from gui import ClientGUI


# Create a new client socket and connect to the server
def create_connection(server_address):
    client = socket.socket(socket.AF_INET,
                           socket.SOCK_STREAM)
    client.connect((server_address))
    return client


# create components, start threads
def run(server_ip, server_port):
    client = create_connection((server_ip, server_port))
    # create a GUI class object, which bears the application loop
    gui = ClientGUI(client)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        run(server_ip, server_port)
    else:
        print('Usage: python3 client.py <serverip> <serverport>')
