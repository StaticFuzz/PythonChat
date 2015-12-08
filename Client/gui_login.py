import tkinter


class LoginScreen(tkinter.Frame):
    def __init__(self, master, callback):
        super().__init__(master)
        self.master = master
        self.callback = callback

        self.display_message = tkinter.Label(self, text="Login or Signup", height=5, width=45)
        self.division_frame = tkinter.Frame(self)

        self.label_frame = tkinter.Frame(self.division_frame)
        self.name_label = tkinter.Label(self.label_frame, text="Username:")
        self.pass_label = tkinter.Label(self.label_frame, text="Password:")

        self.entry_frame = tkinter.Frame(self.division_frame)
        self.pass_entry = tkinter.Entry(self.entry_frame)
        self.name_entry = tkinter.Entry(self.entry_frame)

        self.button_frame = tkinter.Frame(self)
        self.choose_login = tkinter.Button(self.button_frame,
                                           text="LOGIN",
                                           command=lambda: self.callback("LOGIN"))
        self.choose_signup = tkinter.Button(self.button_frame,
                                            text="SIGN UP",
                                            command=lambda: self.callback("SIGNUP"))

    def pack_children(self):
        self.display_message.pack()
        self.division_frame.pack()

        self.label_frame.pack(side=tkinter.LEFT)
        self.name_label.pack(anchor="e", pady=(0, 10))
        self.pass_label.pack(anchor="e")

        self.entry_frame.pack(side=tkinter.LEFT, padx=(5, 63))
        self.name_entry.pack(anchor="w", pady=(0, 10))
        self.pass_entry.pack(anchor="w")

        self.button_frame.pack(pady=20)
        self.choose_login.pack(side="left", padx=2)
        self.choose_signup.pack(side="right", padx=2)


def test_callback(event):
    print(event)


if __name__ == "__main__":
    window = tkinter.Tk()
    login = LoginScreen(window, test_callback)
    login.pack()
    login.pack_children()
    window.mainloop()
