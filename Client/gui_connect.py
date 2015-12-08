import tkinter


class ConnectScreen(tkinter.Frame):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback

        self.connect_message = tkinter.Label(self, text="Enter Server Information", height=5, width=45)
        self.container = tkinter.Frame(self)

        self.label_frame = tkinter.Label(self.container)
        self.ip_label = tkinter.Label(self.label_frame, text="Address:")
        self.port_label = tkinter.Label(self.label_frame, text="Port: ")

        self.entry_frame = tkinter.Frame(self.container)
        self.ip_entry = tkinter.Entry(self.entry_frame)
        self.port_entry = tkinter.Entry(self.entry_frame)

        self.button_frame = tkinter.Frame(self)
        self.connect_button = tkinter.Button(self.button_frame,
                                             text="CONNECT",
                                             command=self.callback)

    def pack_children(self):
        self.connect_message.pack()
        self.container.pack()

        self.label_frame.pack(side=tkinter.LEFT)
        self.ip_label.pack(anchor="e", pady=(0, 10))
        self.port_label.pack(anchor="e")

        self.entry_frame.pack(side=tkinter.LEFT, padx=(0, 60))
        self.ip_entry.pack(anchor="w", pady=(0, 10))
        self.port_entry.pack(anchor="w")

        self.button_frame.pack(pady=20)
        self.connect_button.pack()


def test_callback():
    pass

if __name__ == "__main__":
    window = tkinter.Tk()
    connect = ConnectScreen(window, test_callback)
    connect.pack()
    connect.pack_children()
    window.mainloop()
