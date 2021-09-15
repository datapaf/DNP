from xmlrpc.server import SimpleXMLRPCServer
import os
import sys


def send_file(filename, data):
    
    if os.path.isfile(filename):
        print(f'{filename} not saved')
        return False

    with open(filename, 'wb') as file:
        file.write(data.data)
        print(f'{filename} saved')
        return True


def list_files():
    
    filenames = os.listdir()
    filenames.remove('server.py')

    return filenames


def delete_file(filename):
    
    if not os.path.isfile(filename):
        print(f'{filename} not deleted')
        return False

    os.remove(filename)
    return True


def get_file(filename):
    
    if not os.path.isfile(filename):
        print(f'No such file: {filename}')
        return False

    with open(filename, 'rb') as file:
        print(f'File send: {filename}')
        return file.read()


def parse_command(command):
    operator, raw_left_operand, raw_right_operand = command.split(' ')
    left_operand = float(raw_left_operand)
    right_operand = float(raw_right_operand)
    return operator, left_operand, right_operand


def calculate(expression):

    try:

        operator, left_operand, right_operand = parse_command(expression)

        object_to_return = list()

        if operator == '*':
            result = left_operand * right_operand
        elif operator == '/':    
            result = left_operand / right_operand
        elif operator == '-':
            result = left_operand - right_operand
        elif operator == '+':
            result = left_operand + right_operand
        elif operator == '>':
            result = left_operand > right_operand
        elif operator == '<':
            result = left_operand < right_operand
        elif operator == '>=':
            result = left_operand >= right_operand
        elif operator == '<=':
            result = left_operand <= right_operand
        else:
            print(f'{expression} -- not done')
            return [False, 'No such operation']

        print(f'{expression} -- done')

        if result.is_integer():
            object_to_return.append(int(result))
        else:
            object_to_return.append(result)

        return object_to_return

    except Exception as e:
        print(f'{expression} -- not done')
        return (False, 'Division by zero')


if __name__ == '__main__':

    SERVER_IP = sys.argv[1]
    SERVER_PORT = int(sys.argv[2])
    SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)

    try:

        with SimpleXMLRPCServer(SERVER_ADDRESS) as server:

            server.register_function(send_file)
            server.register_function(list_files)
            server.register_function(delete_file)
            server.register_function(get_file)
            server.register_function(calculate)

            server.serve_forever()

    except KeyboardInterrupt:
        
        print('Server is stopping')
        sys.exit(0)

