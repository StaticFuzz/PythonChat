class Messenger(object):
    """
    messages will be preceded by their length(in bytes not char). The length will be
    encoded using struct.

    :param connection: a socket object that can use send() and recv(). Either
                       a TCP socket, or bound UDP.
    :param structure: a struct.struct() object for packing message length values
    """
    def __init__(self, connection, structure):
        self.length_struct = structure
        self.size = self.length_struct.size
        self.connection = connection

    def recv(self):
        message_length = self.connection.recv(self.size)
        if message_length:
            (message_length,) = self.length_struct.unpack(message_length)
            incoming = b""
            while message_length:
                incoming += self.connection.recv(message_length)
                message_length -= len(incoming)
            return incoming.decode()
        else:
            return message_length

    def send(self, message, connection=None):
        if connection is None:
            connection = self.connection

        message = message.encode()
        message_length = self.length_struct.pack(len(message))

        connection.send(message_length)
        connection.send(message)

    def broadcast(self, connections, message):
        for user in connections:
            client = connections[user]
            try:
                self.send(message, connection=client)
            except ConnectionResetError:
                client.close()


if __name__ == "__main__":
    pass