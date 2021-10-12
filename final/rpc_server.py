import queue
from xmlrpc.server import SimpleXMLRPCServer

SERVER_ADDRESS = ('localhost', 50000)

class Queue:

    q = list()

    def put(self, item: str):
        try:
            self.q.append(item)
        except:
            return False

        return True

    
    def pop(self):
        if self.size() == 0:
            return None

        return self.q.pop(0)


    def pick(self):
        if self.size() == 0:
            return None

        return self.q[0]


    def size(self):
        return len(self.q)


if __name__ == "__main__":

    queue = Queue()

    with SimpleXMLRPCServer(SERVER_ADDRESS, allow_none=True) as server:
        
        server.register_function(queue.put)
        server.register_function(queue.pick)
        server.register_function(queue.pop)
        server.register_function(queue.size)

        server.serve_forever()
