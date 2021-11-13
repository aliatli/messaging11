import json
import struct
import threading


class Receiver:
    def __init__(self, processor, app_socket):
        self.processor = processor
        self.socket = app_socket
        self.encode_format = 'UTF-8'
        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()

    def receive_n(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def recv_msg(self, sock):
        # Read message length and unpack it into an integer
        raw_msglen = self.receive_n(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        if 0 == msglen:
            return None
        # Read the message data
        return self.receive_n(sock, msglen)

    # function to receive messages
    def receive(self):
        while True:
            try:
                message = self.recv_msg(self.socket).decode(self.encode_format)
                message = json.loads(message)
                self.processor.push_back(message)

            except Exception as e:
                # an error will be printed on the command line or console if there's an error
                print(e.args)
                print("exception occured, closing connection...")
                self.socket.close()
                break