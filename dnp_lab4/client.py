import socket
import sys


MAX_BUFF_SIZE = 1024


def send_string(socket, string):
	
	socket.send( bytes(string, 'utf-8') )	


def receive_string(socket):

	raw_bytes = socket.recv(MAX_BUFF_SIZE)
	return raw_bytes.decode('utf-8')


def get_range():

	while True:
		
		left_bound, right_bound = map(int, input().split(' '))
		
		if left_bound < 0 or right_bound < 0 or left_bound >= right_bound:
			print('Enter the range:')
			continue

		break

	return f'{left_bound} {right_bound}'


if __name__ == '__main__':

	try:

		# getting the server address
		try:
			SERVER_IP = sys.argv[1]
			SERVER_PORT = int(sys.argv[2])
			SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
		except:
			print('Usage example: python ./client.py <address> <port>')
			sys.exit(0)

		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		try:
			client_socket.connect(SERVER_ADDRESS)
		except:
			print('Server is unavailable')
			sys.exit(0)

		new_port = receive_string(client_socket)

		if new_port == 'The server is full':
			print('The server is full')
			sys.exit(0)

		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.connect((SERVER_IP, int(new_port)))

		welcome_msg = receive_string(client_socket)
		print(welcome_msg)

		range_msg = get_range()
		send_string(client_socket, range_msg)

		attempts_msg = receive_string(client_socket)
		print(attempts_msg)

		while True:

			guessed_number = input()
			send_string(client_socket, guessed_number)

			raw_results = receive_string(client_socket)
			results = raw_results.split('|')
			
			print(results[0])

			if len(results) == 1:
				if results[0] == 'You win!' or results[0] == 'You lose':
					break
			else:
				print(results[1])
	except socket.error:
		print('Connection lost')
		sys.exit(0)
	except KeyboardInterrupt:
		print('Exit program')
		sys.exit(0)
