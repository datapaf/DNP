import socket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345

sock = socket.socket(
	socket.AF_INET, # Internet
	socket.SOCK_DGRAM # UDP
)


def send_command(command):
	sock.sendto(
		bytes(command, 'utf-8'),
		(SERVER_IP, SERVER_PORT)
	)


def receive_answer():
	data, addr = sock.recvfrom(1024)
	return data.decode("utf-8") 


def bye():
	print('\nbye')


if __name__ == '__main__':
	
	try:
		while True:
			command = input()
			if command.lower() != 'quit':
				send_command(command)
				print(receive_answer())
			else:
				bye()
				break
	except KeyboardInterrupt:
		bye()
