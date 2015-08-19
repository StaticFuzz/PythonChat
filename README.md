# PythonChat
# Python3

PythonChat is a barebones chat server/client with no username/password storage, or any kind of encryption.
It is only dependent on the python standard library, so there should be no issues as long as you have Python 3.x.

Modules:
socket
tkinter(chat_client_tcp.py)
sys    (chat_client_tcp.py)
_thread(chat_server_tcp.py)

Messaging:
messages between the client and srever are formated as such:

  (message length)backtick(message)
  "12`Hello World!"

chat_server_tcp.py:
the server script will create a socket to accept incoming connection requests from clients. After the connection
is accepted and the client socket has been created, each client will be run in it's own thread. Currently there is
no way to specify a port outside of changing the value in the script. It's set to ("0.0.0.0"/"",64321)

chat_client_tcp.py:
the client will create socket and attempt to connect with the server address. If the attempt fails, the program will
close. If successful the tkinter GUI will be created. 

The only function that runs outside of the tkinter mainloop()is handle_incoming(). handle_incoming() is called 
within the mainloop as an .after() event every half second. Ifthere is nothing to read from the client socket it
will block for .25 seconds.

This blocking can cause issues with the tkinter GUI. Because the mainloop() is blocked the GUI will not update.
User actions like moving the window or entering text into the chat entry can seem choppy/delayed. If this is
noticable the blocking time can be lowered:

  client.settimeout(.10) for example.
  
currently there is no way to specify a server(address,port) outside of changing the script. Current target server
is ("127.0.0.1", 64321)
