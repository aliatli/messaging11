import json
import threading
import time
from tkinter import *

import common
from processor import ClientProcessor, ServerProcessor
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
        self.label_head = Label(self.Window,
                                bg=self.bg,
                                fg=self.fg,
                                text=self.name,
                                font="Helvetica 13 bold",
                                pady=5)
        self.line = Label(self.Window,
                          width=450,
                          bg="#ABB2B9")
        self.label_bottom = Label(self.Window,
                                  bg="#ABB2B9",
                                  height=80)
        self.message_entry_box = Entry(self.label_bottom,
                                       bg=self.bg,
                                       fg=self.fg,
                                       font="Helvetica 13", insertbackground=self.fg)
        self.search_button = Button(self.label_bottom,
                                    text="Search",
                                    font="Helvetica 10 bold",
                                    width=20,
                                    bg="#ABB2B9",
                                    command=lambda: self.on_search_clicked(self.message_entry_box.get()))
        self.send_message_button = Button(self.label_bottom,
                                          text="Send",
                                          font="Helvetica 10 bold",
                                          width=20,
                                          bg="#ABB2B9",
                                          command=lambda: self.on_send_clicked(self.message_entry_box.get()))
        self.message_box = Text(self.Window,
                                width=20,
                                height=2,
                                bg=self.bg,
                                fg=self.fg,
                                font="Helvetica 14",
                                padx=5,
                                pady=5)

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

        self.label_head.place(relwidth=1)

        self.line.place(relwidth=1,
                        rely=0.07,
                        relheight=0.012)

        self.message_box.place(relheight=0.745,
                               relwidth=1,
                               rely=0.08)

        self.label_bottom.place(relwidth=1,
                                rely=0.825)

        # place the given widget
        # into the gui window
        self.message_entry_box.place(relwidth=0.50,
                                     relheight=0.06,
                                     rely=0.008,
                                     relx=0.011)

        self.message_entry_box.focus()

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

    # show search result on a different window
    def show_search_result(self, results):
        now = int(time.time())
        filename = self.name + str(now) + '.txt'
        fullpath = []
        # write results to file
        with open(filename, 'w') as json_file:
            fullpath = json_file.name
            json.dump(results, json_file,
                      indent=4,
                      separators=(',', ': '))

        # insert messages to text box
        self.message_box.config(state=NORMAL)
        self.message_box.insert(END, "Search result is written to file: " + fullpath)
        self.message_box.config(state=DISABLED)

        # write message body to terminal
        for r in results:
            if r.get('BODY'):
                print(str(r['BODY']))

    # search button handler
    def on_search_clicked(self, msg):
        pass

    # function to dispatch a sender
    def on_send_clicked(self, msg):
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
        if common.check_valid_json(msg) and common.check_valid_query(msg):
            # convert it to json
            msg = common.convert_to_json(self.socket, msg, 'ClientQueryMessage')
        else:
            return

        # send json message
        common.send_message(self.socket, msg)

    # function to dispatch a sender
    def on_send_clicked(self, msg):
        self.message_box.config(state=DISABLED)
        # put sender name info to the message
        json_msg = common.convert_to_json(self.socket, msg, 'ClientMessage')

        # clear the text entry
        self.message_entry_box.delete(0, END)

        sender_thread = threading.Thread(target=common.send_message, args=(self.socket, json_msg))
        # to not worry about joining
        sender_thread.setDaemon(True)
        sender_thread.start()


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
        if common.check_valid_json(msg) and common.check_valid_query(msg):
            # convert it to json
            msg = common.convert_to_dict(self.socket, msg, 'ServerQueryMessage')
        else:
            print("Invalid Search String Crafted!")
            return

        # do not send msg handle it in processor
        self.processor.push_back(msg)

    # function to dispatch a sender
    def on_send_clicked(self, msg):
        self.message_box.config(state=DISABLED)
        # put sender name info to the message
        json_msg = common.convert_to_json(self.socket, msg, 'ServerMessage')
        dict_msg = common.convert_to_dict(self.socket, msg, 'ServerMessage')
        # delegate database ops to processor
        self.processor.push_back(dict_msg)
        self.message_entry_box.delete(0, END)

        sender_thread = threading.Thread(target=common.send_message, args=(self.socket, json_msg))
        # to not worry about joining
        sender_thread.setDaemon(True)
        sender_thread.start()
