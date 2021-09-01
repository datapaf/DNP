from threading import Thread
import random
import socket
import sys


MAX_BUFF_SIZE = 1024
clients_online = 0


def send_string(socket, string):
	
	socket.send( bytes(string, 'utf-8') )	


def receive_string(socket):

	raw_bytes = socket.recv(MAX_BUFF_SIZE)
	return raw_bytes.decode('utf-8')


def receive_range(client_connection_socket):

	raw_range = receive_string(client_connection_socket)
	return map(int, raw_range.split(' '))


def play_game(client_connection_socket):
	
	send_string(
		client_connection_socket,
		'Welcome to the number guessing game!\nEnter the range:'
	)

	left_bound, right_bound = receive_range(client_connection_socket)

	number = random.randint(left_bound, right_bound)

	isWin = False

	send_string(client_connection_socket, 'You have 5 attempts')

	for i in range(5):

		guessed_number = int(receive_string(client_connection_socket))

		if guessed_number == number:
			isWin = True
			break

		if number < guessed_number:
			send_string(client_connection_socket, f'Less|You have {5-(i+1)} attempts')
		if number > guessed_number:
			send_string(client_connection_socket, f'Greater|You have {5-(i+1)} attempts')
		

	if isWin:
		send_string(client_connection_socket, 'You win!')
	else:
		send_string(client_connection_socket, 'You lose')


def thread_procedure(main_thread_client_con_sock):

	global clients_online

	thread_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	thread_socket.bind((SERVER_IP, 0))

	new_thread_port = thread_socket.getsockname()[1]
	send_string(main_thread_client_con_sock, str(new_thread_port))
	main_thread_client_con_sock.close()

	try:
		thread_socket.listen()
		thread_socket.settimeout(5)
		client_connection_socket, _ = thread_socket.accept()
		play_game(client_connection_socket)
	except socket.timeout:
		clients_online -= 1
		return

	clients_online -= 1


if __name__ == '__main__':

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# getting the port number
	try:
		SERVER_PORT = int(sys.argv[1])
		SERVER_IP = 'localhost'
		SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
	except:
		print('Usage example: python ./server.py <port>')
		sys.exit(0)

	# binding
	try:
		server_socket.bind(SERVER_ADDRESS)
	except:
		print('Error while binding to the specified port')
		sys.exit(0)

	print(f'Starting the server on {SERVER_IP}:{SERVER_PORT}')

	server_socket.listen()

	while True:
		print('Waiting for a connection')

		client_connection_socket, _ = server_socket.accept()
		clients_online += 1

		if clients_online > 2:
			send_string(client_connection_socket, 'The server is full')
			client_connection_socket.close()
			continue

		print('Client connected')

		new_thread = Thread(target=thread_procedure, args=(client_connection_socket, ))
		new_thread.start()


