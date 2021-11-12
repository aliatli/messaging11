import struct
import threading
from tkinter import *
from tkinter import font
from tkinter import ttk

# GUI class for the chat

FORMAT = 'utf-8'
BATCH_SIZE = 1000

class GUI:
    # constructor method
    def __init__(self, name, client, addr):
        self.bg = "#000000"
        self.fg = "#EAECEE"
        self.name = name
        self.client = client
        self.addr = addr

        # chat window which is currently hidden
        self.Window = Tk()
        self.Window.withdraw()
        self.goAhead(self.name)
        self.Window.mainloop()

    def goAhead(self, name):
        self.layout(name)

        # the thread to receive messages
        rcv = threading.Thread(target=self.receive)
        rcv.start()

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

    # function to basically start the thread for sending messages
    def sendButton(self, msg):
        self.message_box.config(state=DISABLED)
        self.msg = msg
        self.entryMsg.delete(0, END)
        snd = threading.Thread(target=self.sendMessage)
        snd.start()

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
                message = self.recv_msg(self.client).decode(FORMAT)

                if None is message:
                    continue
                else:
                    # insert messages to text box
                    self.message_box.config(state=NORMAL)

                    # in case the text is large the gui freezes,
                    # show just beginning and end
                    if len(message) // BATCH_SIZE > 2:
                        # # insert beginning end and
                        self.message_box.insert(END, message[0:BATCH_SIZE])
                        self.message_box.insert(END, "...\n\n")
                        self.message_box.insert(END, message[-BATCH_SIZE:])
                        self.message_box.insert(END, "\n\n")
                    else:
                        self.message_box.insert(END, message + "\n\n")

                    self.message_box.config(state=DISABLED)
                    self.message_box.see(END)
            except Exception as e:
                # an error will be printed on the command line or console if there's an error
                print(e)
                print("exception occured, closing connection...")
                self.client.close()
                break

    # function to send messages
    def sendMessage(self):
        self.message_box.config(state=DISABLED)
        while True:
            message = bytes(f"{self.addr}: {self.msg}", FORMAT)
            # Prefix each message with a 4-byte length (network byte order)
            message = struct.pack('>I', len(message)) + message
            self.client.send(message)
            break
