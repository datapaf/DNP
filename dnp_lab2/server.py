import socket

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
EXCEPTION_MSG = 'Operation cannot be performed'

receiving_sock = socket.socket(
    socket.AF_INET, # Internet
    socket.SOCK_DGRAM # UDP
)
receiving_sock.bind((SERVER_IP, SERVER_PORT))

sending_sock = socket.socket(
    socket.AF_INET, # Internet
    socket.SOCK_DGRAM # UDP
)


def send_answer(result, address):
    sending_sock.sendto(
        bytes(result, "utf-8"),
        (address[0], address[1])
    )


def receive_command():
    raw_data, addr = receiving_sock.recvfrom(1024)
    data = raw_data.decode("utf-8")
    return data, addr


def parse_command(command):
    operator, raw_left_operand, raw_right_operand = command.split(' ')
    left_operand = float(raw_left_operand)
    right_operand = float(raw_right_operand)
    return operator, left_operand, right_operand


def calculate(command):
    try:

        operator, left_operand, right_operand = parse_command(command)

        if operator == '*':
            result = left_operand * right_operand 
            if result.is_integer():
                return int(result)
            else:
                return result
        elif operator == '/':
            result = left_operand / right_operand 
            if result.is_integer():
                return int(result)
            else:
                return result
        elif operator == '-':
            result = left_operand - right_operand 
            if result.is_integer():
                return int(result)
            else:
                return result
        elif operator == '+':
            result = left_operand + right_operand 
            if result.is_integer():
                return int(result)
            else:
                return result
        elif operator == '>':
            return left_operand > right_operand
        elif operator == '<':
            return left_operand < right_operand
        elif operator == '>=':
            return left_operand >= right_operand
        elif operator == '<=':
            return left_operand <= right_operand
        else:
            return EXCEPTION_MSG

    except:
        return EXCEPTION_MSG 


if __name__ == '__main__':
    
    while True:
        command, client_address = receive_command()
        result = calculate(command)
        send_answer(str(result), client_address)
    