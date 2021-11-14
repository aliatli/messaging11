import sys
import socket
import threading

from gui import ServerGUI


# Create a server socket and bind it to given port
def create_connection(server_address):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(server_address)
    return server


# function to start the connection
def start_chat(address):
    print("server is working on " + str(address))
    server_sock = create_connection(address)

    # listening for connections
    server_sock.listen()
    while True:
        # accept connections and the address bound to it
        conn, _ = server_sock.accept()

        # Start the handling thread
        thread = threading.Thread(target=run, args=(conn,))
        thread.start()


def run(conn):
    # create a GUI class object
    gui = ServerGUI(conn)


if __name__ == "__main__":
    if len(sys.argv) == 3:
        server_ip = sys.argv[1]
        server_port = int(sys.argv[2])
        start_chat((server_ip, server_port))
    elif len(sys.argv) == 2:
        server_port = int(sys.argv[1])
        start_chat(('0.0.0.0', server_port))
    else:
        print('Usage: python3 server.py <serverip>|<> <serverport>')
