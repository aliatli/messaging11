import queue
from enum import Enum


# denotes message types
class MessageType(Enum):
    ChatMessage = 1
    QueryMessage = 2
    QueryResultMessage = 3


# class representing the event loop
class Processor:
    def __init__(self, gui):
        self.gui = gui
        # multi producer multi consumer queue
        self.message_queue = queue.Queue(maxsize=100)
        self.is_running = True

    # start waiting for queue to deplete
    def stop_processor(self):
        self.is_running = False

    # push message to the queue
    def push_back(self, message):
        # put blocks until a free spot is found
        self.message_queue.put(message)

    # get type of message
    def get_message_type(self, message):
        if message['TYPE'] == 'ChatMessage':
            return MessageType.ChatMessage
        elif message['TYPE'] == 'QueryMessage':
            return MessageType.QueryMessage
        elif message['TYPE'] == 'QueryResultMessage':
            return MessageType.QueryResultMessage
        else:
            return None

    # execute one iteration
    def process_message(self):
        message = self.message_queue.get()
        message_type = self.get_message_type(message)

        # python 3.10 introduces match-case but what if you don't have it
        if message_type is MessageType.ChatMessage:
            self.gui.add_received_message(message['BODY'])
        else:
            pass

    # start processing message queue elements
    def start(self):
        while self.is_running() or not self.message_queue.empty():
            self.process_message()

        # stop called and no more jobs
        print("Stop requested, finished all events.")
        self.message_queue.join()
