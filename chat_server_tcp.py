import socket
import _thread


def main():
    """
    creates a socket object(server) that will accept incoming client
    connection requests. Each client socket will be run in it's own
    thread. Currently socket address is ("",64321).
    """
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
        client_dict[address] = client_socket
        print("{} connected".format(address))
        _thread.start_new_thread(thread_client, (client_socket, address, client_dict))


def thread_client(conn, addr, clients):
    """
    Main client loop. Accepts messages from client socket then
    broadcasts message to all clients. If the connection is broken
    the loop will break, and the client will be deleted from client_dict.
    """
    lock = _thread.allocate_lock()
    while conn:
        try:
            message = get_message(conn)
        except socket.error:
            print("bad connection at {}".format(addr))
            break

        if message:
            print("{}: {}".format(addr, message))
            server_broadcast(message, clients)
        else:
            break

    lock.acquire()
    del clients[addr]
    lock.release()


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

    for addr in clients:
        client = clients[addr]
        try:
            client.send(out_msg)
        except socket.error or ConnectionResetError:
            continue


if __name__ == "__main__":
    main()
