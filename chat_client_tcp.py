import socket
from tkinter import *
import sys


class Chat(Frame):
    def __init__(self, window, sock):
        super().__init__(self, window)

        self.chat_display = Text(self)
        self.chat_display.insert(END, "Welcome to chat!\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.pack(fill=BOTH, expand=True)

        self.scroll = Scrollbar(self.chat_display)
        self.scroll.pack(side=RIGHT, fill=Y)
        self.chat_display.config(yscrollcommand=self.scroll.set)

        self.chat_entry = Entry(self, width=76)
        self.chat_entry.pack(side=LEFT)
        self.chat_entry.bind("<Return>", lambda x: handle_out_going(self, sock))
        """
        lambda needs a parameter(x) to store the info tkinter
        sends about the bound event(<return>)
        """

        self.get_entry = Button(self, text="SEND",command=lambda: handle_out_going(self, sock))
        self.get_entry.pack(side=LEFT, fill=Y)

    def add_message(self, message):
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
    client.settimeout(.25)

    try:
        client.connect(server)
        print("Connected with {}".format(server))
    except socket.error as err:
        print(err)
        print("unable to connect with server...\n\nexiting...")
        sys.exit()

    window = Tk()
    window.protocol("WM_DELETE_WINDOW", destroy_all(client, window))
    window.geometry("500x300")
    window.title("Chat Client")

    chat_window = Chat(window, client)
    chat_window.after(500, handle_incoming(client, chat_window))
    chat_window.mainloop()


def handle_out_going(chat_object, connection):
    """
    reads from the chat_entry and sends it to the server.
    message formatting is :

    (message_length)backtick(messsage) as one string

    event is unused. Tkinter sends information about the
    bound event. the function needed a way to except the
    information so as not to raise an error.
    """
    message = chat_object.chat_entry.get()
    chat_object.chat_entry.delete(0, END)
    out_msg = "{}`{}".format(len(message), message)
    connection.send(out_msg.encode())


def handle_incoming(connection, chat_object):
    """
    called every 500 milliseconds from within the
    tkinter mainloop. Will check for incoming socket
    data, but will pass if socket timeout limit is
    reached.
    """
    try:
        temp_message = connection.recv(4096).decode()
        length, message = temp_message.split("`")
        length = int(length) - len(message)
        while len_message > 0:
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
        chat_object.after(500, handle_incoming)


def destroy_all(connection, chat_object):
    chat_object.destroy()
    connection.close()
    sys.exit()


if __name__ == "__main__":
    main()
