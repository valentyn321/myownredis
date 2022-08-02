from gevent import socket
from gevent.pool import Pool
from gevent.server import StreamServer

from collections import namedtuple
from io import BytesIO
from socket import error as socket_error


# Exceptions to notify theconnection-handling loop of problems
class CommandError(Exception):
    pass


class Disconnect(Exception):
    pass


Error = namedtuple("Error", ("message",))


class ProtocolHandler(object):
    def handle_request(self, socket_file):
        """Parses a request from the client into it's component parts"""
        pass

    def write_response(self, socket_file, data):
        """Serializes the response data and sends it to the client"""
        pass


class Server(object):
    def __init__(self, host="127.0.0.1", port=31337, max_clients=64) -> None:
        self._pool = Pool(max_clients)
        self._server = StreamServer(
            (host, port),
            self.connection_handler,
            spawn=self._pool,
        )

        self._protocol = ProtocolHandler()
        self._kv = {}

    def connection_handler(self, connection, address):
        # Convert a socket object into file-like object
        socket_file = connection.makefile("rwb")

        # Process client's requests until client disconnects.
        while True:
            try:
                data = self._protocol.handle_request(socket_file)
            except Disconnect:
                break

            try:
                resp = self.get_response(data)
            except CommandError as exc:
                resp = Error(exc.args[0])

            self._protocol.write_response(socket_file, resp)

    def get_response(self, data):
        """Upacks the data sent by the client, execute the
        command he specified and pass back the return value"""
        pass

    def run(self):
        self._server.serve_forever()
