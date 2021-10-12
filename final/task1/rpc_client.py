from xmlrpc.client import ServerProxy

if __name__ == "__main__":
    
    try:
        with ServerProxy(f"http://127.0.0.1:{50000}") as proxy:

            while True:

                command = input("Enter command: ").split()

                if command[0] == "put":
                    item = command[1]
                    proxy.put(item)
                elif command[0] == "pick":
                    print(proxy.pick())
                elif command[0] == "pop":
                    print(proxy.pop())
                elif command[0] == "size":
                    print(proxy.size())
    except KeyboardInterrupt:
        print('closing')
