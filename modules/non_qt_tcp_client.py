# non Qt TCP client
# https://docs.python.org/3/howto/sockets.html
# The purpose of this is to show that non-Qt sockets
# can communicate with Qt sockets. THe docking station
# and cloudplugs will most likely NOT have any form
# of Qt on them

import socket
import time
from enum import Enum

MSGLEN = 256

class MyTcpSocketState(Enum):
    DISCONNECTED = 0
    CONNECTED = 1

class MySocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

        self.state: MyTcpSocketState = MyTcpSocketState.DISCONNECTED

    def connect(self, host, port):
        host_port_tuple = (host, port)
        self.sock.connect(host_port_tuple)
        self.state = MyTcpSocketState.CONNECTED
    
    def mysend(self, msg):
        totalsent = 0

        while totalsent < MSGLEN:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("Socket connection broken")
            totalsent += sent

    def myreceive(self):
        chunks = []
        bytes_recd = 0
        while bytes_recd < MSGLEN:
            chunk = self.sock.recv(min(MSGLEN - bytes_recd, 2048))
            if chunk == b'':
                raise RuntimeError("Socket connection broken")
            chunks.append(chunk)
            bytes_recd += len(chunk)
        
        return b''.join(chunks)

    def handle_server_disconnect(self):
        # If connection is lost, change the state of the
        # socket object and close the current socket.
        # Re-create it and let the driver code attempt
        # to reconnect
        print('Lost connection to server...')
        self.state = MyTcpSocketState.DISCONNECTED
        self.sock.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def main():
    s = MySocket()

    while True:
        print(f'Above disconnected loop, {s.state = }')
        while s.state == MyTcpSocketState.DISCONNECTED:
            try:
                s.connect('127.0.0.1', 20100)

            except Exception as ex:
                print(ex)

            time.sleep(1)

        print(f'Above connected loop, {s.state = }')
        while s.state == MyTcpSocketState.CONNECTED:
            
            msg = "NON_QT_TEST"
            try:
                s.mysend(msg.encode())
            except BrokenPipeError as ex:
                s.handle_server_disconnect()
                break

            time.sleep(1)



if __name__ == '__main__':
    main()
    