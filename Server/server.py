import socket
import _thread
import sqlite3
import os
import struct

from urllib.request import urlopen
from messenger import Messenger
from Server.database import make_database, new_user, username_check


def main():
    """
    creates a socket object(server) that will accept incoming client
    connection requests. Each client socket will be run in it's own
    thread.
    """

    active_clients = {}  # dictionary used to store all active clients and their socket objects

    # load database of users and passwords or create if it doesn't exist
    database_exists = os.path.isfile("users.db")
    db_conn = sqlite3.connect("users.db", check_same_thread=False)
    if not database_exists:
        make_database(db_conn)

    # default address and port
    host_address = "0.0.0.0"
    host_port = 54321

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Try binding to default port 54321, if taken increment by one until successful bind
    while True:
        try:
            server.bind((host_address, host_port))
            break
        except socket.error:  # Address already in use
            host_port += 1

    server.listen(5)

    # get external ip address from ipify.org.
    try:
        data = urlopen("https://api.ipify.org")
        external_ip = data.read().decode()
        data.close()
    except:
        print("Unable to retrieve external I.P. address")
        external_ip = "unknown"

    print("\n\nListening at:\nADDRESS {}\nPORT {}".format(external_ip, host_port))

    # main server loop accepts incoming client connections and passes them to a new thread
    while True:
        client_socket, address = server.accept()
        print("{} connected".format(address))
        _thread.start_new_thread(thread_client, (client_socket, address, db_conn, active_clients))


def thread_client(conn, addr, db_conn, active_clients):
    """
    Checks and verifies password/username, and handles adding new
    users to the database.

    Main client loop Accepts messages from client socket then
    broadcasts message to all clients. If the connection is broken
    the loop will break, database will be updated(active state).

    :param conn: socket objected connected with remote client
    :param addr: tuple of the remote clients address and port
    :param db_conn: connection to the sqlite3 database containing user-info
    """

    length_struct = struct.Struct("!I")
    local_messenger = Messenger(conn, length_struct)
    lock = _thread.allocate_lock()
    verified = False  # used to control looping

    while not verified:  # handle client login/signup credentials
        try:
            """
            first message received will be a login or sign up attempt
            message_type will be "LOGIN" or "SIGNUP"
            """
            message = local_messenger.recv()
            message_type, username, password = message.split("`", 2)
        except ValueError or ConnectionResetError:
            print("bad connection at {}".format(addr))
            break

        # retrieve user info from database. username_check() returns two boolean values
        lock.acquire()
        username_exists, correct_password = username_check(db_conn, username, password)
        lock.release()

        # add new users to database
        if message_type == "SIGNUP":
            if username_exists:  # username already taken
                local_messenger.send("UNAVAILABLE")
            else:
                # acquire lock and add user to database and active_clients
                lock.acquire()
                new_user(db_conn, username, password)
                active_clients[username] = conn
                lock.release()

                local_messenger.send("OK")
                verified = True

        # login existing users
        elif message_type == "LOGIN":
            if username_exists and correct_password:
                if username not in active_clients:  # username is not already signed in
                    # acquire lock and add username to active_clients
                    lock.acquire()
                    active_clients[username] = conn
                    lock.release()

                    local_messenger.send("OK")
                    verified = True
                else:
                    local_messenger.send("USER_ACTIVE")  # user is already active
            else:
                local_messenger.send("BAD")  # wrong password or username

    while verified:
        """
        client will only be verified when an existing username and password have been
        submitted, or a new username and password has been created.

        verified loop will handle all incoming messages, errors, socket closures
        """
        try:
            message = local_messenger.recv()
        except socket.error or struct.error:
            print("bad connection at {}".format(addr))
            break

        if message:
            lock.acquire()
            local_messenger.broadcast(active_clients, message)
            lock.release()
        else:
            # empty string signaling connection closed
            lock.acquire()
            del active_clients[username]
            lock.release()
            conn.close()
            break

    # clean up after client disconnects or the connection is broken
    if username in active_clients:
        lock.acquire()
        del active_clients[username]
        lock.release()
    conn.close()
    print("{} DISCONNECTED".format(addr))


if __name__ == "__main__":
    main()
