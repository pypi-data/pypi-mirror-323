import argparse
import asyncio
import gc
import os.path
import pathlib
import socket
import ssl
from typing import Union, Tuple, Any, Optional,Self

PRINT: int = 0


async def echo_server(loop: asyncio.AbstractEventLoop, 
                     address: Union[str, Tuple[str, int]], 
                     unix: bool) -> None:
    if unix:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(address)
    sock.listen(5)
    sock.setblocking(False)
    if PRINT:
        print('Server listening at', address)
    with sock:
        while True:
            client, addr = await loop.sock_accept(sock)
            if PRINT:
                print('Connection from', addr)
            loop.create_task(echo_client(loop, client))


async def echo_client(loop: asyncio.AbstractEventLoop, 
                     client: socket.socket) -> None:
    try:
        client.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (OSError, NameError):
        pass

    with client:
        while True:
            data = await loop.sock_recv(client, 1000000)
            if not data:
                break
            await loop.sock_sendall(client, data)
    if PRINT:
        print('Connection closed')


async def echo_client_streams(reader: asyncio.StreamReader, 
                            writer: asyncio.StreamWriter) -> None:
    sock = writer.get_extra_info('socket')
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    except (OSError, NameError):
        pass
    if PRINT:
        print('Connection from', sock.getpeername())
    while True:
        data = await reader.read(1000000)
        if not data:
            break
        writer.write(data)
    if PRINT:
        print('Connection closed')
    writer.close()


class EchoProtocol(asyncio.Protocol):
    def __init__(self) -> None:
        self.transport: Optional[asyncio.BaseTransport] = None

    def connection_made(self: Self, transport: asyncio.BaseTransport) -> None:
        self.transport = transport

    def connection_lost(self, exc: Optional[Exception]) -> None:
        self.transport = None

    def data_received(self, data: bytes) -> None:
        if self.transport:
            self.transport.write(data)


class EchoBufferedProtocol(asyncio.BufferedProtocol):
    def __init__(self: Self) -> None:
        self.transport: Optional[asyncio.WriteTransport] = None
        self.buffer: bytearray = bytearray(256 * 1024)

    def connection_made(self: Self, transport: asyncio.WriteTransport) -> None:
        self.transport = transport

    def connection_lost(self: Self, exc: Optional[Exception]) -> None:
        self.transport = None

    def get_buffer(self: Self, sizehint: int) -> bytearray:
        return self.buffer

    def buffer_updated(self: Self, nbytes: int) -> None:
        if self.transport:
            self.transport.write(self.buffer[:nbytes])


async def print_debug(loop: asyncio.AbstractEventLoop) -> None:
    while True:
        print(chr(27) + "[2J")  # clear screen
        await asyncio.sleep(0.5)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--uvloop', default=False, action='store_true')
    parser.add_argument('--streams', default=False, action='store_true')
    parser.add_argument('--proto', default=False, action='store_true')
    parser.add_argument('--addr', default='127.0.0.1:25000', type=str)
    parser.add_argument('--print', default=False, action='store_true')
    parser.add_argument('--ssl', default=False, action='store_true')
    parser.add_argument('--buffered', default=False, action='store_true')
    args: argparse.Namespace = parser.parse_args()

    if args.uvloop:
        import uvloop
        loop: asyncio.AbstractEventLoop = uvloop.new_event_loop()
        print('using UVLoop')
    else:
        loop = asyncio.new_event_loop()
        print('using asyncio loop')

    asyncio.set_event_loop(loop)
    loop.set_debug(False)

    if args.print:
        PRINT = 1

    if hasattr(loop, 'print_debug_info'):
        loop.create_task(print_debug(loop))
        PRINT = 0

    unix: bool = False
    addr: Union[str, Tuple[str, int]]
    if args.addr.startswith('file:'):
        unix = True
        addr = args.addr[5:]
        if os.path.exists(addr):
            os.remove(addr)
    else:
        addr_parts = args.addr.split(':')
        addr = (addr_parts[0], int(addr_parts[1]))

    print('serving on: {}'.format(addr))

    server_context: Optional[ssl.SSLContext] = None
    if args.ssl:
        print('with SSL')
        if hasattr(ssl, 'PROTOCOL_TLS'):
            server_context = ssl.SSLContext(ssl.PROTOCOL_TLS)
        else:
            server_context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
        server_context.load_cert_chain(
            (pathlib.Path(__file__).parent.parent.parent /
                'tests' / 'certs' / 'ssl_cert.pem'),
            (pathlib.Path(__file__).parent.parent.parent /
                'tests' / 'certs' / 'ssl_key.pem'))
        if hasattr(server_context, 'check_hostname'):
            server_context.check_hostname = False
        server_context.verify_mode = ssl.CERT_NONE

    srv: Any
    if args.streams:
        if args.proto:
            print('cannot use --stream and --proto simultaneously')
            exit(1)

        if args.buffered:
            print('cannot use --stream and --buffered simultaneously')
            exit(1)

        print('using asyncio/streams')
        if unix:
            coro = asyncio.start_unix_server(echo_client_streams,
                                             addr,
                                             ssl=server_context)
        else:
            coro = asyncio.start_server(echo_client_streams,
                                        addr[0], addr[1],
                                        ssl=server_context)
        srv = loop.run_until_complete(coro)
    elif args.proto:
        if args.streams:
            print('cannot use --stream and --proto simultaneously')
            exit(1)

        protocol: Union[Type[EchoProtocol], Type[EchoBufferedProtocol]]
        if args.buffered:
            print('using buffered protocol')
            protocol = EchoBufferedProtocol
        else:
            print('using simple protocol')
            protocol = EchoProtocol

        if unix:
            coro = loop.create_unix_server(protocol, addr,
                                           ssl=server_context)
        else:
            coro = loop.create_server(protocol, addr[0], addr[1],
                                      ssl=server_context)
        srv = loop.run_until_complete(coro)
    else:
        if args.ssl:
            print('cannot use SSL for loop.sock_* methods')
            exit(1)

        print('using sock_recv/sock_sendall')
        loop.create_task(echo_server(loop, addr, unix))
    try:
        loop.run_forever()
    finally:
        if hasattr(loop, 'print_debug_info'):
            gc.collect()
            print(chr(27) + "[2J")
            loop.print_debug_info()

        loop.close()
