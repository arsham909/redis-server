import socket  # noqa: F401
from  threading import Thread

class Redis():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.running = True
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
                while True:
                    respond = self.process_request(connection)
                    connection.sendall(respond)
            
            except ConnectionResetError as e:
                pass
            except Exception as e:
                print(e)
    
    
    def process_request(self, connection):
        
        raw_request  = connection.recv(1024).decode()
        if not raw_request:
            return b''
        line = b""
        output = {}
        test = []
        RESP_array = raw_request.split("\r\n")
        element_numbers = RESP_array[0].split("*",1)[1]
        print(element_numbers)
        bulk_string = "".join(RESP_array[1:-1])
        datas = bulk_string.split("$", int(element_numbers))[1:]
        for data in datas:
            number = ''
            for s in data:
                if s.isdigit():
                    number += s
                else:
                    break
            test.append(data[len(number) :])  
        output['command'] = test[0].lower()
        output['value'] = test[1]
        if output['command'] == "ping":
            return  b"+PONG\r\n"
        elif output['command'] == "echo":
            respond = f"${len(output['value'])}\r\n{output['value']}\r\n"
            return respond.encode()
        
        
        



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
    server_socket = Redis("localhost", 6379)

if __name__ == "__main__":
    main()
