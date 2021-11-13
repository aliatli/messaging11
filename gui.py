import datetime
import struct
import threading
import time
from datetime import timezone
from tkinter import *
import json

from processor import Processor
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
        self.processor = Processor(self)
        self.receiver = Receiver(self.processor, self.socket)
        self.start_loop(self.name)

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
        self.labelHead = Label(self.Window,
                               bg=self.bg,
                               fg=self.fg,
                               text=self.name,
                               font="Helvetica 13 bold",
                               pady=5)

        self.labelHead.place(relwidth=1)
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

        self.labelBottom = Label(self.Window,
                                 bg="#ABB2B9",
                                 height=80)

        self.labelBottom.place(relwidth=1,
                               rely=0.825)

        self.entryMsg = Entry(self.labelBottom,
                              bg=self.bg,
                              fg=self.fg,
                              font="Helvetica 13")

        # place the given widget
        # into the gui window
        self.entryMsg.place(relwidth=0.50,
                            relheight=0.06,
                            rely=0.008,
                            relx=0.011)

        self.entryMsg.focus()

        # create a Send Button
        self.buttonMsg = Button(self.labelBottom,
                                text="Send",
                                font="Helvetica 10 bold",
                                width=20,
                                bg="#ABB2B9",
                                command=lambda: self.sendButton(self.entryMsg.get()))

        # create a Send Button
        self.buttonSearch = Button(self.labelBottom,
                                   text="Search",
                                   font="Helvetica 10 bold",
                                   width=20,
                                   bg="#ABB2B9",
                                   command=lambda: self.sendButton(self.entryMsg.get()))

        self.buttonMsg.place(relx=0.505,
                             rely=0.008,
                             relheight=0.06,
                             relwidth=0.245)
        self.buttonSearch.place(relx=0.75,
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

    # function to dispatch a sender
    def sendButton(self, msg):
        self.message_box.config(state=DISABLED)
        self.msg = self.convert_to_json(msg, 'ChatMessage')
        self.entryMsg.delete(0, END)

        sender_thread = threading.Thread(target=self.sendMessage)
        # to not worry about joining
        sender_thread.setDaemon(True)
        sender_thread.start()

    # function that does sending
    def sendMessage(self):
        self.message_box.config(state=DISABLED)
        while True:
            message = bytes(f"{self.msg}", FORMAT)
            # Prefix each message with a 4-byte length (network byte order)
            message = struct.pack('>I', len(message)) + message
            self.socket.send(message)
            break
