import datetime
import struct
import threading
import time
from datetime import timezone
from tkinter import *
import json

from processor import Processor, ClientProcessor, ServerProcessor
from receiver import Receiver

FORMAT = 'utf-8'
BATCH_SIZE = 1000


class GUI:
    # constructor method
    def __init__(self, name, app_socket):
        self.bg = "#000000"
        self.fg = "#EAECEE"
        self.name = name
        self.socket = app_socket

        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.start_loop(self.name)

    # this needs to be the last call from main, otherwise wont show
    def start_loop(self, name):
        self.layout(name)
        self.Window.mainloop()

    # The main layout of the chat
    def layout(self, name):

        self.name = name
        # to show chat window
        self.Window.deiconify()
        self.Window.title("Messaging")
        self.Window.resizable(width=True,
                              height=True)
        self.Window.configure(width=470,
                              height=550,
                              bg=self.bg)
        self.label_head = Label(self.Window,
                                bg=self.bg,
                                fg=self.fg,
                                text=self.name,
                                font="Helvetica 13 bold",
                                pady=5)

        self.label_head.place(relwidth=1)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.message_box = Text(self.Window,
                                width=20,
                                height=2,
                                bg=self.bg,
                                fg=self.fg,
                                font="Helvetica 14",
                                padx=5,
                                pady=5)

        self.message_box.place(relheight=0.745,
                               relwidth=1,
                               rely=0.08)

        self.label_bottom = Label(self.Window,
                                  bg="#ABB2B9",
                                  height=80)

        self.label_bottom.place(relwidth=1,
                                rely=0.825)

        self.message_entry_box = Entry(self.label_bottom,
                                       bg=self.bg,
                                       fg=self.fg,
                                       font="Helvetica 13")

        # place the given widget
        # into the gui window
        self.message_entry_box.place(relwidth=0.50,
                                     relheight=0.06,
                                     rely=0.008,
                                     relx=0.011)

        self.message_entry_box.focus()

        # create a Send Button
        self.send_message_button = Button(self.label_bottom,
                                          text="Send",
                                          font="Helvetica 10 bold",
                                          width=20,
                                          bg="#ABB2B9",
                                          command=lambda: self.on_send_clicked(self.message_entry_box.get()))

        # create a Send Button
        self.search_button = Button(self.label_bottom,
                                    text="Search",
                                    font="Helvetica 10 bold",
                                    width=20,
                                    bg="#ABB2B9",
                                    command=lambda: self.on_search_clicked(self.message_entry_box.get()))

        self.send_message_button.place(relx=0.505,
                                       rely=0.008,
                                       relheight=0.06,
                                       relwidth=0.245)
        self.search_button.place(relx=0.75,
                                 rely=0.008,
                                 relheight=0.06,
                                 relwidth=0.245)

        self.message_box.config(cursor="arrow")

        # create a scroll bar
        scrollbar = Scrollbar(self.message_box)

        # place the scroll bar
        # into the gui window
        scrollbar.place(relheight=1,
                        relx=0.974)

        scrollbar.config(command=self.message_box.yview)

        self.message_box.config(state=DISABLED)

    # add received dictionary object to message box
    def add_received_message(self, message):
        if None is message:
            return
        else:
            # insert messages to text box
            self.message_box.config(state=NORMAL)
            message_body = message['BODY']
            message_sender = message['SENDER']
            epoch_time = message['EPOCH_TIME']
            gmt_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(epoch_time))
            self.message_box.insert(END, str(message_sender) + " @ " + gmt_time + ":\n")

            # in case the text is large the gui freezes, so show just beginning and end
            if len(message_body) // BATCH_SIZE > 2:
                # insert to beginning and end
                self.message_box.insert(END, message_body[0:BATCH_SIZE])
                self.message_box.insert(END, "...\n\n")
                self.message_box.insert(END, message_body[-BATCH_SIZE:])
                self.message_box.insert(END, "\n\n")
            else:
                self.message_box.insert(END, message_body + "\n\n")

            self.message_box.config(state=DISABLED)
            self.message_box.see(END)

    # convert text message to json with meta-data
    def convert_to_json(self, message, type):
        # python native representation
        dictionary_representation = {'TYPE': type,
                                     'EPOCH_TIME': int(time.time()),
                                     'SENDER': self.socket.getsockname(),
                                     'RECEIVER': self.socket.getpeername(),
                                     'BODY': message}
        # convert it to json object
        return json.dumps(dictionary_representation, ensure_ascii=False)

    # check if query string is valid json
    def check_valid_json(self, msg):
        try:
            json.loads(msg)
        except ValueError as e:
            print(e.args)
            return False
        return True

    # check if json is a valid query
    # example {"HISTORY_DEPTH":"10", "DIRECTION":"BOTH", "SEARCH_STRING":"a"}
    def check_valid_query(self, msg):
        dict_obj = json.loads(msg)

        # it must have these fields.
        if dict_obj.get('HISTORY_DEPTH') is None \
                or dict_obj.get('SEARCH_STRING') is None \
                or dict_obj.get('DIRECTION') is None \
                or len(dict_obj.keys()) != 3:
            return False

        # history depth can be non-negative integer or 'ALL'
        if not dict_obj['HISTORY_DEPTH'].isdigit() and not dict_obj['HISTORY_DEPTH'] == 'ALL':
            return False
        if dict_obj['HISTORY_DEPTH'].isdigit() and int(dict_obj['HISTORY_DEPTH']) == 0:
            return False

        # direction can have up, down and both values only
        if dict_obj['DIRECTION'] != 'UP' and dict_obj['DIRECTION'] != 'DOWN' and dict_obj['DIRECTION'] != 'BOTH':
            return False

        # search_string can have any value, empty string means to not apply this filter
        return True

    # show search result on a different window
    def pop_search_result(self, message):
        print(message)

    # search button handler
    def on_search_clicked(self, msg):
        pass

    # function to dispatch a sender
    def on_send_clicked(self, msg):
        pass

    # function that does sending
    def send_message(self, json_msg):
        pass

# client gui
class ClientGUI(GUI):

    def __init__(self, app_socket):
        self.processor = ClientProcessor(self)
        self.receiver = Receiver(self.processor, app_socket)
        super().__init__("client", app_socket)

    # search button handler
    def on_search_clicked(self, msg):
        self.message_box.config(state=DISABLED)
        msg = msg.upper()
        # if a valid json and a valid query
        if self.check_valid_json(msg) and self.check_valid_query(msg):
            # convert it to json
            msg = self.convert_to_json(msg, 'ClientQueryMessage')
        else:
            return

        # send json message
        self.send_message(msg)

    # function to dispatch a sender
    def on_send_clicked(self, msg):
        self.message_box.config(state=DISABLED)
        # put sender name info to the message
        json_msg = self.convert_to_json(msg, 'ClientMessage')

        # clear the text entry
        self.message_entry_box.delete(0, END)

        sender_thread = threading.Thread(target=self.send_message, args=(json_msg,))
        # to not worry about joining
        sender_thread.setDaemon(True)
        sender_thread.start()

    # function that does sending
    def send_message(self, json_msg):
        self.message_box.config(state=DISABLED)
        while True:
            message = bytes(f"{json_msg}", FORMAT)
            # Prefix each message with a 4-byte length (network byte order)
            message = struct.pack('>I', len(message)) + message
            self.socket.send(message)
            break


# client gui
class ServerGUI(GUI):

    def __init__(self, app_socket):
        self.processor = ServerProcessor(self)
        self.receiver = Receiver(self.processor, app_socket)

        super().__init__("server", app_socket)

    # search button handler
    def on_search_clicked(self, msg):
        self.message_box.config(state=DISABLED)
        msg = msg.upper()
        # if a valid json and a valid query
        if self.check_valid_json(msg) and self.check_valid_query(msg):
            # convert it to json
            msg = self.convert_to_json(msg, 'ServerQueryMessage')
        else:
            print("Invalid Search String Crafted!")
            return

        # do not send msg handle it in processor
        self.processor.push_back(msg)

    # function to dispatch a sender
    def on_send_clicked(self, msg):
        self.message_box.config(state=DISABLED)
        json_msg = []
        # put sender name info to the message
        json_msg = self.convert_to_json(msg, 'ServerMessage')

        self.message_entry_box.delete(0, END)

        sender_thread = threading.Thread(target=self.send_message, args=(json_msg,))
        # to not worry about joining
        sender_thread.setDaemon(True)
        sender_thread.start()

    # function that does sending
    def send_message(self, json_msg):
        self.message_box.config(state=DISABLED)
        while True:
            # delegate database ops to processor
            self.processor.push_back(json_msg)
            message = bytes(f"{json_msg}", FORMAT)
            # Prefix each message with a 4-byte length (network byte order)
            message = struct.pack('>I', len(message)) + message
            self.socket.send(message)
            break
