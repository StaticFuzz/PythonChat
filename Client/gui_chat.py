import tkinter


class ChatScreen(tkinter.Frame):
    def __init__(self, master, callback):
        super().__init__(master)
        self.callback = callback

        self.chat_frame = tkinter.Frame(self, border=10)
        self.scroll = tkinter.Scrollbar(self.chat_frame)
        self.chat_display = tkinter.Text(self.chat_frame, height=25, width=90)
        self.chat_display.insert(tkinter.END, "Welcome to chat!\n")
        self.chat_display.config(yscrollcommand=self.scroll.set, state="disabled")
        self.scroll.config(command=self.chat_display.yview)
        self.chat_entry = tkinter.Entry(self, width=80)
        self.chat_entry.bind("<Return>", self.callback)
        self.get_entry = tkinter.Button(self, text="SEND", command=self.callback)

    def pack_children(self):
        self.chat_frame.pack(fill="both", expand=1)
        self.scroll.pack(side="right", fill="y")
        self.chat_display.pack(fill="both", expand=1)
        self.chat_entry.pack(side="left", fill="both", expand=1, pady=(0, 10), padx=(10, 0))
        self.get_entry.pack(side="left", expand=0, pady=(0, 10), padx=(0, 10))

    def add_message(self, message):
        """
        Adds message to chat display
        """
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", message + "\n\n")
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")  # automatically scroll down as messages are added
        self.chat_display.update_idletasks()


def test_callback():
    pass


if __name__ == "__main__":
    window = tkinter.Tk()
    chat = ChatScreen(window, test_callback)
    chat.pack()
    chat.pack_children()
    window.mainloop()
