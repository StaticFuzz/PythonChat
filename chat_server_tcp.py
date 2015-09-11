import socket
import _thread
import json


def main():
    """
    creates a socket object(server) that will accept incoming client
    connection requests. Each client socket will be run in it's own
    thread. Currently socket address is ("",64321).
    """
    json_file = open("users", "r")
    user_data = json.load(json_file)
    json_file.close()

    host_address = ""
    host_port = 64321
    client_dict = {}

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host_address, host_port))
    server.listen(5)

    print("Listening at port: {}".format(host_port))

    while True:
        client_socket, address = server.accept()
        print("{} connected".format(address))
        _thread.start_new_thread(thread_client, (client_socket, address, client_dict, user_data))


def thread_client(conn, addr, clients, users):
    """
    Checks and verifies password/username, and handles adding new
    users to the database.

    Main client loop Accepts messages from client socket then
    broadcasts message to all clients. If the connection is broken
    the loop will break, and the client will be deleted from client_dict.
    """
    MESSAGE_OK = "{}`{}".format(len("OK"), "OK")
    MESSAGE_UNAVAILABLE = "{}`{}".format(len("UNAVAILABLE"), "UNAVAILABLE")
    MESSAGE_BAD = "{}`{}".format(len("BAD"), "BAD")
    MESSAGE_USER_ACTIVE = "{}`{}".format(len("USER ACTIVE"), "USER ACTIVE")

    lock = _thread.allocate_lock()
    verified = False

    while not verified:
        try:
            message = get_message(conn)
            message_type, username, password = message.split("`", 2)
        except ValueError:
            print("bad connection at {}".format(addr))
            break

        if message_type == "SIGNUP":
            if username in users:
                conn.send(MESSAGE_UNAVAILABLE.encode())
            else:
                lock.acquire()
                users[username] = password
                clients[username] = [conn, addr]
                json_file = open("users", "wt")
                json_file.write(json.dumps(users))
                json_file.close()
                lock.release()
                conn.send(MESSAGE_OK.encode())
                verified = True
        elif message_type == "LOGIN":
            if username in users and users[username] == password:
                if username not in clients:
                    lock.acquire()
                    clients[username] = [conn, addr]
                    lock.release()
                    conn.send(MESSAGE_OK.encode())
                    verified = True
                else:
                    conn.send(MESSAGE_USER_ACTIVE.encode())
            else:
                conn.send(MESSAGE_BAD.encode())

    while verified:
        try:
            message = get_message(conn)
        except socket.error:
            print("bad connection at {}".format(addr))
            lock.acquire()
            del clients[username]
            lock.release()
            conn.close()
            break

        if message:
            print("{}: {}".format(addr, message))
            server_broadcast(message, clients)
        else:
            lock.acquire()
            del clients[username]
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


def server_broadcast(msg, clients):
    """
    Broadcasts message to each connected client in client_dict(global)
    clients(local). No socket errors will be raised. Closing sockets
    is handled by the thread running the client.

    message format is; (message_length)backtick(message)
    """
    out_msg = "{}`{}".format(len(msg), msg).encode()

    for user in clients:
        client = clients[user][0]
        try:
            client.send(out_msg)
        except ConnectionResetError:
            continue


if __name__ == "__main__":
    main()
