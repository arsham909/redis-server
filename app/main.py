import asyncio

class Redis():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.store: dict[str, list[str]|str] = {}
        self.list = {}
    
    async def start_server(self):
        server = await asyncio.start_server(self._handle_client, self.host, self.port)
        print(f"Server is open on port {self.port}")
        async with server:
            await server.serve_forever()
    
    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter): 
        try:
            while True:
                data = await reader.read(1024)
                if not data: break
                respond = await self._dispatch(self._parse_resp(data.decode()))
                writer.write(respond)
                await writer.drain()
        except ConnectionResetError as e:
            pass
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:  
            writer.close()
            await writer.wait_closed() 
    
    
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
        for _ in range(element_numbers):
            tokens.append(parts[i+1])
            i += 2
        return tokens
    
    async def _dispatch(self, tokens: list[str]) -> bytes:
        
        if not tokens:
            return b"ERR empty command"
        
        command = tokens[0].upper()
        
        if command== "PING":
            return  b"+PONG\r\n"
        
        elif command == "ECHO" and len(tokens) >= 2:
            print(self.list)
            return f"${len(tokens[1])}\r\n{tokens[1]}\r\n".encode()
        
        elif command == "SET" and len(tokens) >= 3:
            key, value = tokens[1] , tokens[2]
            self.store[key] = value
            if len(tokens) >= 5 :
                asyncio.create_task(self._expire_key(key, tokens[3], tokens[4]))
            return b"+OK\r\n"
        
        elif command == "GET" and len(tokens) >= 2:
            if value:=self.store.get(tokens[1], None):
                return f"${len(value)}\r\n{value}\r\n".encode()
            return b"$-1\r\n"
        
        elif command == "RPUSH" and len(tokens) >= 3:
            key = tokens[1] 
            elements = tokens[2:]
            if key not in self.list:
                self.list[key] = []
            self.list[key].extend(elements)
            respond = f":{len(self.list[key])}\r\n"
            return respond.encode()
        
        elif command == "LRANGE" and len(tokens) == 4 :
            try:
                key, start, stop= tokens[1], int(tokens[2]), int(tokens[3])
                if key not in self.list:
                    return b"*0\r\n"
                length = len(self.list[key])
                if  (start >= length or start > stop) and (stop > 0 and start > 0) :
                    return b"*0\r\n"
                elif key in self.list and stop >= length or stop == -1:
                    return self._list_values(key, start, length)
                else:
                    return self._list_values(key,start, stop)
                    
            except Exception as e:
                print(e)
            
        
        return b"-ERR unknown command\r\n"
            
    async def _expire_key(self, key, unit, duration):
        try:
            seconds = float(duration)
            if unit == "PX":
                seconds /= 1000
            await asyncio.sleep(seconds)    
            
            if key in self.store:
                del self.store[key]
        except Exception as e :
            print(f"[EXPIRE ERROR] {e}")   
    
    def _list_values(self, key, start, stop) -> bytes:
        list_values = self.list[key]
        if abs(stop) > len(list_values): stop = 0
        return self._encode_resp(list_values[start:stop+1])

    
    def _encode_resp(self, values: list) -> bytes:
        respond = "*0\r\n"
        try:
            if values:
                respond = f"*{len(values)}\r\n"
                respond += ''.join([f"${len(i)}\r\n{i}\r\n" for i in values])
        except  Exception as e:
            print(e)
        return respond.encode()
                       

        
        
async def main():
    print("Logs from your program will appear here!")
    server_socket = Redis("localhost", 6379)
    await server_socket.start_server()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
