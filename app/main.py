import socket  # noqa: F401
from  threading import Thread
import asyncio

class Redis():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.start_server()
    
    def start_server(self):
        with socket.create_server((self.host, self.port), reuse_port=True) as server:
            print(f"Server is open on port {self.port}")
            while self.running:
                connection, address = server.accept()
                thread = Thread(target=self.handle_client, args=(connection,))
                thread.start()
    
    def handle_client(self, connection):
        with connection:
            try:
                raw_request = connection.recv(1024).decode()
                if not raw_request:
                    return
                connection.sendall(b"+PONG\r\n")
            
            except Exception as e:
                print(e)
                
        



def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment the code below to pass the first stage
    #
    # server_socket = socket.create_server(("localhost", 6379), reuse_port=True)
    # connection, _ = server_socket.accept() # wait for client
    # while True:
    #     connection.recv(1024).decode()
    #     connection.sendall(b"+PONG\r\n")
    server_socket = Redis(("localhost", 6379), reuse_port=True)

if __name__ == "__main__":
    main()
