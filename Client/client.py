import socket
import tkinter
import sys
import struct

from messenger import Messenger
from Client.gui_connect import ConnectScreen
from Client.gui_login import LoginScreen
from Client.gui_chat import ChatScreen


def destroy_all(connection, application):
    application.destroy()
    connection.close()
    sys.exit()


class App(tkinter.Tk):
    def __init__(self):
        super().__init__()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.protocol("WM_DELETE_WINDOW", lambda: destroy_all(self.connection, self))
        self.title("Chat Client")

        self.length_struct = struct.Struct("!I")
        self.messenger = Messenger(self.connection, self.length_struct)

        self.username = ""
        self.password = ""

        self.connect = ConnectScreen(self, self.connect_to_server)
        self.login = LoginScreen(self, self.check_data)
        self.chat = ChatScreen(self, self.handle_out_going)

        self.connect.pack()
        self.connect.pack_children()

    def connect_to_server(self):
        """
        Callback for self.connect. Retrieves the user submitted address
        and port. Attempts to make connection. If any errors are caught the
        connect_message widget will be updated with information about the error.
        """
        host_address = self.connect.ip_entry.get()
        host_port = self.connect.port_entry.get()

        try:
            host_port = int(host_port)
            self.connection.connect((host_address, host_port))
            self.connect.pack_forget()
            self.login.pack()
            self.login.pack_children()
        except ValueError:
            self.connect.connect_message.config(text="Invalid Entry For Port\nMust Be an Integer", fg="red")
        except ConnectionRefusedError:
            self.connect.connect_message.config(text="Server Refused Connection", fg="red")
        except socket.gaierror:
            self.connect.connect_message.config(text="Invalid Address", fg="red")

    def check_data(self, message_type):
        """
        Communicates with chat server to verify login information. If the
        login or sign up attempt fails a message is displayed on the login
        screen.

        :param message_type: tells the server whether it is a login attempt
        or signup request
        """
        self.username = self.login.name_entry.get()
        self.password = self.login.pass_entry.get()

        # restrict user names to alpha numeric values
        if not self.username.isalnum():
            self.login.display_message.config(text="Username can only be numbers and letters", fg="red")
            return

        # format message to be sent
        message = "{}`{}`{}".format(message_type, self.username, self.password)
        reply = ""

        # try communicating with server
        try:
            self.messenger.send(message)
            reply = self.messenger.recv()
        except ConnectionResetError or ValueError:
            self.login.display_message.config(text="Connection with server lost...restarting", fg="red")
            self.login.pack_forget()
            self.connection.detach()
            self.connect.pack()

        # check for all possible server responses
        if reply == "OK":
            self.login.pack_forget()
            self.title(self.username)
            self.chat.pack()
            self.chat.pack_children()
            self.connection.settimeout(.10)  # prevents blocking calls of handle_incoming()
            self.handle_incoming()
        elif reply == "UNAVAILABLE":
            self.login.display_message.config(text="Username Unavailable", fg="red")
        elif reply == "BAD":
            self.login.display_message.config(text="Incorrect user Info", fg="red")
        elif reply == "USER ACTIVE":
            self.login.display_message.config(text="Username is currently already logged in", fg="red")
        else:
            self.login.display_message.config(text="Unexpected Server Response")

    def handle_out_going(self, event=None):
        """
        reads from the chat_entry and sends it to the server.

        :param event: is used as a place holder for the event
        information sent by self.chat_entry.bind(<RETURN>) it is not
        used.
        """
        text = self.chat.chat_entry.get()

        if text:  # prevent empty messages from being sent
            try:
                message = "{}: {}".format(self.username, text)  # This should be handled by server
                self.messenger.send(message)
                self.chat.chat_entry.delete(0, "end")
            except ConnectionResetError:
                self.chat.pack_forget()
                self.login.pack()
                self.login.display_message.config(text="Connection with server lost")

    def handle_incoming(self):
        """
        called every 500 milliseconds from within the
        tkinter mainloop. Will check for incoming socket
        data, but will pass if socket timeout limit is
        reached.
        """
        try:
            message = self.messenger.recv()
            self.chat.add_message(message)
        except socket.timeout:
            pass
        except ConnectionResetError or struct.error:
            self.chat.pack_forget()
            self.login.pack()
            self.login.display_message.config(text="Connection with server lost")
            return
        finally:
            self.after(500, self.handle_incoming)


if __name__ == "__main__":
    chat = App()
    chat.mainloop()
