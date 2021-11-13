import queue
import threading
from enum import Enum

import common
from persistency_layer import Persistency


# denotes message types
class MessageType(Enum):
    ClientMessage = 1
    ServerMessage = 2
    ClientQueryMessage = 3
    ServerQueryMessage = 4
    QueryResult = 5


# class representing the event loop
class Processor:
    def __init__(self, gui):
        self.gui = gui
        # multi producer multi consumer queue
        self.message_queue = queue.Queue(maxsize=100)
        self.is_running = True
        self.thread = threading.Thread(target=self.start)
        self.thread.start()

    # start waiting for queue to deplete
    def stop_processor(self):
        self.is_running = False

    # push message to the queue
    def push_back(self, message):
        # put blocks until a free spot is found
        self.message_queue.put(message)

    # get type of message
    def get_message_type(self, message):
        if message['TYPE'] == 'ClientMessage':
            return MessageType.ClientMessage
        elif message['TYPE'] == 'ServerMessage':
            return MessageType.ServerMessage
        elif message['TYPE'] == 'ClientQueryMessage':
            return MessageType.ClientQueryMessage
        elif message['TYPE'] == 'ServerQueryMessage':
            return MessageType.ServerQueryMessage
        elif message['TYPE'] == 'QueryResult':
            return MessageType.QueryResult
        else:
            return None

    # execute one iteration
    def process_message(self):
        pass

    # start processing message queue elements
    def start(self):
        while self.is_running or not self.message_queue.empty():
            self.process_message()

        # stop called and no more jobs
        print("Halt is requested, finished all events.")
        self.message_queue.join()


# client processor
class ClientProcessor(Processor):

    def __init__(self, gui):
        super().__init__(gui)

    # execute one iteration for client
    def process_message(self):
        message = self.message_queue.get()
        message_type = self.get_message_type(message)

        if message_type is MessageType.ServerMessage:
            # this is received only by the client
            self.gui.add_received_message(message)
        elif message_type is MessageType.QueryResult:
            self.gui.show_search_result(message['BODY'])
        else:
            pass


# server processer
class ServerProcessor(Processor):
    def __init__(self, gui):
        super().__init__(gui)
        self.persistency = Persistency()

    def process_message(self):
        message = self.message_queue.get()
        message_type = self.get_message_type(message)

        if message_type is MessageType.ClientMessage:
            # show on message box
            self.gui.add_received_message(message)
            # save it to the db
            self.persistency.save_message(message)
        elif message_type is MessageType.ServerMessage:
            # save own message to db
            self.persistency.save_message(message)
        elif message_type is MessageType.ServerQueryMessage:
            # ask persistency to execute query
            result = self.persistency.filter_message(message)
            self.gui.show_search_result(result)
        elif message_type is MessageType.ClientQueryMessage:
            # message body bears the query
            message_body = message['BODY']
            # check if format is ok
            if common.check_valid_json(message_body) and common.check_valid_query(message_body):
                results = self.persistency.filter_message(message)
                json_results = common.convert_to_json(self.gui.socket, results, 'QueryResult')
                # then send back to client
                common.send_message(self.gui.socket, json_results)
            else:
                print('Received query message is erroneously crafted!')
        else:
            pass
