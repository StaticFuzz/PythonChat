import socket
import tkinter
import sys


class Chat(tkinter.Frame):
    def __init__(self, window, sock):
        tkinter.Frame.__init__(self, window)
        self.pack(fill="both", expand=1)
        self.connection = sock
        self.window = window
        self.username = ""
        self.password = ""

        # widgets for connect display(entering server info)
        self.connect_frame = tkinter.Frame(self)
        self.connect_message = tkinter.Label(self.connect_frame, text="Enter Server Information", height=5, width=45)
        self.ip_label = tkinter.Label(self.connect_frame, text="Address:")
        self.ip_entry = tkinter.Entry(self.connect_frame)
        self.port_label = tkinter.Label(self.connect_frame, text="Port: ")
        self.port_entry = tkinter.Entry(self.connect_frame)
        self.connect_button_frame = tkinter.Frame(self.connect_frame)
        self.connect_button = tkinter.Button(self.connect_button_frame,
                                             text="CONNECT",
                                             command=self.connect_to_server)

        # widgets for login display
        self.login_frame = tkinter.Frame(self)
        self.display_message = tkinter.Label(self.login_frame, text="Login or Signup", height=5, width=45)
        self.name_label = tkinter.Label(self.login_frame, text="Username:")
        self.name_entry = tkinter.Entry(self.login_frame)
        self.pass_label = tkinter.Label(self.login_frame, text="Password:")
        self.pass_entry = tkinter.Entry(self.login_frame)
        self.button_frame = tkinter.Frame(self.login_frame)
        self.choose_login = tkinter.Button(self.button_frame,
                                           text="LOGIN",
                                           command=lambda: self.check_data("LOGIN"))
        self.choose_signup = tkinter.Button(self.button_frame,
                                            text="SIGNUP",
                                            command=lambda: self.check_data("SIGNUP"))

        # widgets for main chat display
        self.chat_frame = tkinter.Frame(self, border=10)
        self.scroll = tkinter.Scrollbar(self.chat_frame)
        self.chat_display = tkinter.Text(self.chat_frame, height=25, width=90)
        self.chat_display.insert(tkinter.END, "Welcome to chat!\n")
        self.chat_display.config(yscrollcommand=self.scroll.set, state="disabled")
        self.scroll.config(command=self.chat_display.yview)
        self.chat_entry = tkinter.Entry(self, width=80)
        self.chat_entry.bind("<Return>", self.handle_out_going)
        self.get_entry = tkinter.Button(self, text="SEND", command=self.handle_out_going)

        self.connect()

    def connect(self):
        """
        Packs connect widgets
        """
        self.connect_frame.pack(fill="both", expand=1)
        self.connect_message.pack()
        self.ip_label.pack()
        self.ip_entry.pack()
        self.port_label.pack()
        self.port_entry.pack()
        self.connect_button_frame.pack(pady=20)
        self.connect_button.pack()

    def login(self):
        """
        Packs login widgets
        """
        self.login_frame.pack(fill="both", expand=1)
        self.display_message.pack()
        self.name_label.pack()
        self.name_entry.pack()
        self.pass_label.pack()
        self.pass_entry.pack()
        self.button_frame.pack(pady=20)
        self.choose_login.pack(side="left", padx=2)
        self.choose_signup.pack(side="right", padx=2)

    def connect_to_server(self):
        """
        Attempts to connect to user specified address/port
        """
        host_address = self.ip_entry.get()
        host_port = self.port_entry.get()

        try:
            host_port = int(host_port)
            self.connection.connect((host_address, host_port))
            self.connect_frame.pack_forget()
            self.login()
        except ValueError:
            self.connect_message.config(text="Invalid Entry For Port\nMust Be an Integer", fg="red")
        except ConnectionRefusedError:
            self.connect_message.config(text="Server Refused Connection", fg="red")

    def check_data(self, message_type):
        """
        Communicates with chat server to verify login information

        message_type tells the server weather it is a login attempt
        or signup request
        """
        self.username = self.name_entry.get()
        self.password = self.pass_entry.get()
        message = "{}`{}`{}".format(message_type, self.username, self.password)
        message = "{}`{}".format(len(message), message)
        reply = ""

        self.connection.send(message.encode())

        try:
            reply = self.get_message()
        except socket.error or ValueError:
            self.display_message.config(text="Unable to connect", fg="red")

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

    def make_chat(self):
        """
        Packs widgets for main chat UI
        """
        self.chat_frame.pack(fill="both", expand=1)
        self.scroll.pack(side="right", fill="y")
        self.chat_display.pack(fill="both", expand=1)
        self.chat_entry.pack(side="left", fill="both", expand=1, pady=(0, 10), padx=(10, 0))
        self.get_entry.pack(side="left", expand=0, pady=(0, 10), padx=(0, 10))
        self.update_idletasks()

        self.connection.settimeout(.10)  # prevents blocking calls of handle_incoming()
        self.handle_incoming()

    def handle_out_going(self, event=None):
        """
        reads from the chat_entry and sends it to the server.
        the event parameter is used as a place holder for the event
        information sent by self.chat_entry.bind(<RETURN>) it is not
        used.
        message formatting is :

        (message_length)backtick(messsage) as one string
        """
        message = "{}: {}".format(self.username, self.chat_entry.get())
        self.chat_entry.delete(0, "end")
        outgoing_message = "{}`{}".format(len(message), message)
        self.connection.send(outgoing_message.encode())

    def handle_incoming(self):
        """
        called every 500 milliseconds from within the
        tkinter mainloop. Will check for incoming socket
        data, but will pass if socket timeout limit is
        reached.
        """
        try:
            message = self.get_message()
            self.add_message(message)
        except socket.timeout:
            pass
        except ConnectionResetError or ValueError:
            # ValueError will be raised if the server sends an empty string signaling a closing socket
            print("Connection with server lost...")
            destroy_all(self.connection, self)
        finally:
            self.after(500, self.handle_incoming)

    def add_message(self, message):
        """
        Adds message to chat display
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message + "\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")  # automatically scroll down as messages are added
        self.chat_display.update_idletasks()

    def get_message(self):
        temp_message = self.connection.recv(4096).decode()
        length, message = temp_message.split("`", 1)
        length = int(length) - len(message)
        while length > 0:
            temp_message = self.connection.recv(4096).decode()
            length -= len(temp_message)
            message += temp_message
        return message


def main():
    """
    creates a client socket object to communicate with a chat server
    current target is (127.0.0.1, 64321). Starts a tkinter GUI for
    accepting and displaying chat messages.
    """
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    window = tkinter.Tk()
    window.protocol("WM_DELETE_WINDOW", lambda: destroy_all(client, window))
    window.title("Chat Client")

    chat_window = Chat(window, client)
    chat_window.mainloop()


def destroy_all(connection, chat_object):
    chat_object.destroy()
    connection.close()
    sys.exit()


if __name__ == "__main__":
    main()