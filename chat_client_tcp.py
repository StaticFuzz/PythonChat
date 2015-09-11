import socket
from tkinter import *
import sys


class Chat(Frame):
    def __init__(self, window, sock):
        Frame.__init__(self, window)
        self.pack(fill=BOTH, expand=1)
        self.connection = sock
        self.window = window
        self.username = ""
        self.password = ""

        # widgets for login display
        self.login_frame = Frame(self)
        self.display_message = Label(self.login_frame, text="Login or Signup", height=5, width=45)
        self.name_label = Label(self.login_frame, text="Username:")
        self.name_entry = Entry(self.login_frame)
        self.pass_label = Label(self.login_frame, text="Password:")
        self.pass_entry = Entry(self.login_frame)
        self.button_frame = Frame(self.login_frame)
        self.choose_login = Button(self.button_frame,
                                   text="LOGIN",
                                   command=lambda: self.check_data("LOGIN"))
        self.choose_signup = Button(self.button_frame,
                                    text="SIGNUP",
                                    command=lambda: self.check_data("SIGNUP"))

        # widgets for main chat display
        self.chat_frame = Frame(self)
        self.scroll = Scrollbar(self.chat_frame)
        self.chat_display = Text(self.chat_frame, height=25, width=90, yscrollcommand=self.scroll.set)
        self.chat_display.insert(END, "Welcome to chat!\n")
        self.scroll.config(command=self.chat_display.yview)
        self.chat_display.config(state="disabled")
        self.chat_entry = Entry(self, width=80)
        self.chat_entry.bind("<Return>", lambda x: handle_out_going(self,
                                                                    self.connection,
                                                                    self.username))
        self.get_entry = Button(self, text="SEND", command=lambda: handle_out_going(self,
                                                                                    self.connection,
                                                                                    self.username))

        self.login()

    def make_chat(self):
        """
        Packs widgets for main chat UI
        """
        self.chat_frame.pack(fill=BOTH, expand=1)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.chat_display.pack(fill=BOTH, expand=1)
        self.chat_entry.pack(side=LEFT, fill=BOTH, expand=1)
        self.get_entry.pack(side=LEFT, expand=0)
        self.update_idletasks()

        self.connection.settimeout(.20)
        handle_incoming(self.connection, self)

    def login(self):
        """
        Packs login widgets
        """
        self.login_frame.pack(fill=BOTH, expand=1)
        self.display_message.pack()
        self.name_label.pack()
        self.name_entry.pack()
        self.pass_label.pack()
        self.pass_entry.pack()
        self.button_frame.pack(pady=20)
        self.choose_login.pack(side=LEFT, padx=2)
        self.choose_signup.pack(side=RIGHT, padx=2)

    def check_data(self, message_type):
        """
        Communicates with chat server to verify login information
        """
        self.username = self.name_entry.get()
        self.password = self.pass_entry.get()
        message = "{}`{}`{}".format(message_type, self.username, self.password)
        message = "{}`{}".format(len(message), message)
        reply = ""

        self.connection.send(message.encode())

        try:
            reply = get_message(self.connection)
        except socket.error or ValueError:
            self.display_message.config(text="Unable to connect", fg='red"')

        if reply == "OK":
            self.login_frame.pack_forget()
            self.window.title(self.username)
            self.make_chat()
        elif reply == "UNAVAILABLE":
            self.display_message.config(text="Username Unavailable", fg="red")
        elif reply == "BAD":
            self.display_message.config(text="Incorrect user Info", fg="red")
        elif reply == "USER ACTIVE":
            self.display_message.config(text="Username is currently logged in from another device", fg="red")

    def add_message(self, message):
        """
        Adds message to chat display
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert(END, message + "\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.update_idletasks()


def main():
    """
    creates a client socket object to communicate with a chat server
    current target is (127.0.0.1, 64321). Starts a tkinter GUI for
    accepting and displaying chat messages.
    """
    address = "127.0.0.1"
    port = 64321
    server = (address, port)

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(server)
        print("Connected with {}".format(server))

    except socket.error as err:
        print(err)
        print("unable to connect with server...\n\nexiting...")
        sys.exit()

    window = Tk()
    window.protocol("WM_DELETE_WINDOW", lambda: destroy_all(client, window))
    window.title("Chat Client")

    chat_window = Chat(window, client)
    chat_window.mainloop()


def handle_out_going(chat_object, connection, username):
    """
    reads from the chat_entry and sends it to the server.
    message formatting is :

    (message_length)backtick(messsage) as one string
    """
    message = "{}: {}".format(username, chat_object.chat_entry.get())
    chat_object.chat_entry.delete(0, END)
    outgoing_message = "{}`{}".format(len(message), message)
    connection.send(outgoing_message.encode())


def handle_incoming(connection, chat_object):
    """
    called every 500 milliseconds from within the
    tkinter mainloop. Will check for incoming socket
    data, but will pass if socket timeout limit is
    reached.

    TODO: raise errors on except and let calling functions/classes
    handle errors.
    """
    try:
        temp_message = connection.recv(4096).decode()
        length, message = temp_message.split("`", 1)
        length = int(length) - len(message)
        while length > 0:
            temp_message = connection.recv(4096).decode()
            length -= len(temp_message)
            message += temp_message
        chat_object.add_message(message)
    except socket.timeout:
        pass
    except ConnectionResetError or ValueError:
        print("Connection with server lost...")
        destroy_all(connection, chat_object)
    finally:
        chat_object.after(500, lambda: handle_incoming(connection, chat_object))


def get_message(connection):
    temp_message = connection.recv(4096).decode()
    length, message = temp_message.split("`", 1)
    length = int(length) - len(message)
    while length > 0:
        temp_message = connection.recv(4096).decode()
        length -= len(temp_message)
        message += temp_message
    return message


def destroy_all(connection, chat_object):
    chat_object.destroy()
    connection.close()
    sys.exit()


if __name__ == "__main__":
    main()
