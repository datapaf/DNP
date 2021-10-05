import sys

if __name__ == '__main__':
   
    try:
        
        command = input()

        if command[0] == 'connect':
            address = command[1]
            port = command [2]
        elif command[0] == 'set':
            key = command[1]
            value = command[2]
        elif command[0] == 'get':
            key = command[1]
        elif command[0] == 'quit':
            key = command[1]
            value = command[2]
        else:
            print('no such command')

    except KeyboardInterrupt:
        sys.exit(0)
