import socket
import json
from urllib.request import urlopen
import _thread


def main():
    """
    creates a socket object(server) that will accept incoming client
    connection requests. Each client socket will be run in it's own
    thread. Currently socket address is ("",54321).
    """

    # load json database of users and passwords
    json_file = open("users", "r")
    user_data = json.load(json_file)
    json_file.close()
    active_clients = {}  # used for broadcasting messages to all current connections

    host_address = "0.0.0.0"
    host_port = 54321

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Try binding to default port 54321, if taken increment by one until successful bind
    while True:
        try:
            server.bind((host_address, host_port))
            break
        except socket.error:
            host_port += 1

    server.listen(5)

    # get external ip address from ipify.org
    try:
        data = urlopen("https://api.ipify.org")
        external_ip = data.read().decode()
        data.close()
    except:
        print("Unable to retrieve external I.P. address")
        external_ip = "unknown"

    print("\n\nListening at:\nADDRESS {}\nPORT {}".format(external_ip, host_port))

    # main server loop accepts incoming clients connections and passes them to a new thread
    while True:
        client_socket, address = server.accept()
        print("{} connected".format(address))
        _thread.start_new_thread(thread_client, (client_socket, address, active_clients, user_data))


def thread_client(conn, addr, active_clients, user_data):
    """
    Checks and verifies password/username, and handles adding new
    users to the database.

    Main client loop Accepts messages from client socket then
    broadcasts message to all clients. If the connection is broken
    the loop will break, and the client will be deleted from active_clients.
    """
    MESSAGE_OK= "{}`{}".format(len("OK"), "OK")
    MESSAGE_UNAVAILABLE = "{}`{}".format(len("UNAVAILABLE"), "UNAVAILABLE")
    MESSAGE_BAD = "{}`{}".format(len("BAD"), "BAD")
    MESSAGE_USER_ACTIVE = "{}`{}".format(len("USER ACTIVE"), "USER ACTIVE")

    lock = _thread.allocate_lock()
    verified = False

    while not verified:  # handle client login/signup credentials
        try:
            message = get_message(conn)
            message_type, username, password = message.split("`", 2)
        except ValueError:
            print("bad connection at {}".format(addr))
            break

        # add new users to database
        if message_type == "SIGNUP":
            if username in user_data:  # username already taken
                conn.send(MESSAGE_UNAVAILABLE.encode())
            else:
                lock.acquire()

                # update the loaded json data
                user_data[username] = password

                # update the json database with new user info
                # not sure if this is appropriate way to update a JSON file
                json_file = open("users", "wt")
                json_file.write(json.dumps(user_data))
                json_file.close()

                active_clients[username] = [conn, addr]
                lock.release()
                conn.send(MESSAGE_OK.encode())
                verified = True

        # login existing users
        elif message_type == "LOGIN":
            if username in user_data and user_data[username] == password:
                if username not in active_clients:
                    lock.acquire()
                    active_clients[username] = [conn, addr]
                    lock.release()
                    conn.send(MESSAGE_OK.encode())
                    verified = True
                else:
                    conn.send(MESSAGE_USER_ACTIVE.encode())  # user is already active
            else:
                conn.send(MESSAGE_BAD.encode())  # wrong password

    while verified:
        """
        client will only be verified when an existing username and password have been
        submitted, or a new username and password has been created.

        verified loop will handle all incoming messages, errors, socket closures
        """
        try:
            message = get_message(conn)
        except socket.error:
            print("bad connection at {}".format(addr))
            lock.acquire()
            del active_clients[username]
            lock.release()
            conn.close()
            break

        if message:
            print("{}: {}".format(addr, message))
            server_broadcast(message, active_clients)
        else:
            lock.acquire()
            del active_clients[username]
            lock.release()
            conn.close()
            break


def get_message(connection):
    """
    Returns a message from the specified connection(parameter).
    message format is: (message_length)backtick(message) as one string.
    """
    try:
        temp_message = connection.recv(4096).decode()
        length, message = temp_message.split('`', 1)
        length = int(length) - len(message)
        while length > 0:
            temp_message = connection.recv(4096).decode()
            message += temp_message
            length -= len(temp_message)
        return message
    except ValueError:
        return ""


def server_broadcast(msg, active_clients):
    """
    Broadcasts message to each connected client in client_dict(global)
    clients(local). No socket errors will be raised. Closing sockets
    is handled by the thread running the client.

    message format is; (message_length)backtick(message)
    """
    out_msg = "{}`{}".format(len(msg), msg).encode()

    for user in active_clients:
        client = active_clients[user][0]
        try:
            client.send(out_msg)
        except ConnectionResetError:
            continue


if __name__ == "__main__":
    main()
