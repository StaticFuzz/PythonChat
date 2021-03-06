**CHAT SERVER:**
```
A multi-threaded server for accepting incoming connections and client communication.
Supports client username/password creation and storage. Note that there is no encryption
for messaging or password storage. Information sent in messages or stored in the 
database is not secure.

User credentials are stored in an sqlite database. If the database doesn't exist it will
be created on startup, and the username/password table will be generated. Basic database
queries and insertions/deletions have been wrapped in callable functions(database.py).

The default TCP port is 54321. If the port is already in use, the server will increment 
the port number by 1 until it can successfully bind. This port number will displayed after
the bind along with ip address information. The server is bound to the address "0.0.0.0",
meaning all available interfaces on the host machine. Any clients on the LAN will be able
to connect. Port forwarding will be necessary for accepting connections from outside the
local area network.

There are currently no administrative tools for governing the server, so expect anarchy.
```
**CHAT CLIENT:**
```
A simple GUI interface for sending and receiving messages with a server. The three tkinter
GUIs are stored as self contained python programs, and can be viewed without running 
client.py.

Each GUI has it's own function. gui_connect.py has two entry fields, address and port. 
After a successful connection is made, the user will be asked to submit a username and 
password for a login attempt or new user request. This will be handled with the gui_login.py.
The remaining GUI (gui_chat.py) is the main chat display with an entry field for writing
and a text field for displaying received messages
```
**MESSENGER:**
```
All communication between client and server is dictated by the Messenger class in messenger.py.
A simple protocol is used to insure messages are received correctly. All data sent will be 
preceded by its length. The length is structured using the struct module. The current structure
is "!I" an unsigned int(4 bytes) using network byte order.

There isn't any real exception handling when it comes to communication. If any part of the 
messaging protocol failsand raises an exception the connection will be dropped.
```

