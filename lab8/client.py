from xmlrpc.client import ServerProxy
import sys

if __name__ == '__main__':

    print('The client starts')
   
    node = None

    while True:
        
        try:
            
            command = input().split()

            if command[0] == 'connect':
                address = command[1]
                port = command [2]
                try:
                    node = ServerProxy(f'http://{address}:{port}')
                    print('connected')
                except:
                    print(f'The server {address}:{port} is unavailable.')
            elif command[0] == 'getleader':
                if node == None:
                    print('you need to connect to a node')
                    continue
                print(node.get_leader())
            elif command[0] == 'suspend':
                period = command[1]
                print(f'sleeping for {period} seconds')
                node.suspend(period)
            elif command[0] == 'quit':
                print('The client ends')
                sys.exit(0)
            else:
                print('no such command')

        except KeyboardInterrupt:
            print('The client ends')
            sys.exit(0)
