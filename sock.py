import socket

class socketConnection:
    def __init__(self, host = None, port = None):
        self.host = host
        self.port = port
        self.sock = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self):
        self.close()

    def open(self):
        opened = False
        if self.sock is not None:
            print('Error Socket already open')
            return opened
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(None)
            print(f'Connected to {self.host}:{self.port}')
            opened = True
        except Exception as e:
            if e is socket.timeout:
                print('Socket timed out')
            else:
                print(f'Failed to open socket: {e}')
            self.sock = None
        finally:
            return opened

    def close(self):
        if self.sock:
            try:
                self.sock.close()
                print('Socket closed')
            except Exception as e:
                print(f'Error closing socket: {e}')
            finally:
                self.sock = None

    def get_socket(self):
        if self.sock is None:
            raise RuntimeError("Socket is not open yet.")
        return self.sock

    #assumes message is preencoded, not always the case but is for current project    
    def send_msg(self, encoded_msg):
        self.get_socket().sendall(encoded_msg)

    def recv_msg(self):
        return self.get_socket().recv(1024)

