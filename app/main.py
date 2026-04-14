import socket  # noqa: F401
from  threading import Thread

class Redis():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.store: dict[str, str] = {}
    
    def start_server(self):
        with socket.create_server((self.host, self.port), reuse_port=True) as server:
            print(f"Server is open on port {self.port}")
            while True:
                connection, address = server.accept()
                Thread(target=self._handle_client, args=(connection,)).start()
    
    def _handle_client(self, connection: socket.socket):
        with connection:
            try:
                while True:
                    data = connection.recv(1024).decode()
                    if not data:
                        break
                    response = self._dispatch(self._parse_resp(data))
                    connection.sendall(response)
            except ConnectionResetError as e:
                pass
            except Exception as e:
                print(f"[ERROR] {e}")
    
    def _parse_resp(self, raw: str) -> list[str]:
        """
        Parse a RESP
        Example input: "*2\r\n$3\r\nGET\r\n$3\r\nfoo\r\n"
        Returns: ["GET", "foo"]
        """

        parts = raw.split("\r\n")
        element_numbers = int(parts[0][1:]) # "*4" -> 4      
        tokens = []
        i = 1
        for _ in element_numbers(range(element_numbers)):
            tokens.append(parts[i+1])
            i += 2
        return tokens
    
    def _dispatch(self, tokens: list[str]) -> bytes:
        
        if not tokens:
            return b"ERR empty command"
        
        command = tokens[0].upper()
        
        if command== "PING":
            return  b"+PONG\r\n"
        elif command == "ECHO" and len(tokens) >= 2:
            return f"${len(tokens[1])}\r\n{tokens[1]}\r\n".encode()
        
        
        



def main():
    print("Logs from your program will appear here!")
    server_socket = Redis("localhost", 6379)
    server_socket.start_server()

if __name__ == "__main__":
    main()
