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

    def receive_nbytes(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    def receive_message(self, sock):
        # Read message length and unpack it into an integer
        raw_message_len = self.receive_nbytes(sock, 4)
        if not raw_message_len:
            return None
        message_len = struct.unpack('>I', raw_message_len)[0]
        if 0 == message_len:
            return None
        # Read the message data
        return self.receive_nbytes(sock, message_len)

    # function to receive messages
    def receive(self):
        while True:
            try:
                # waits all the payload is received
                message = self.receive_message(self.socket).decode(self.encode_format)
                # from json string to native dictionary
                message = json.loads(message)
                self.processor.push_back(message)

            except Exception as e:
                # an error will be printed on the command line or console if there's an error
                print(e.args)
                print("exception occurred, closing connection...")
                self.socket.close()
                break
