from multithreading import Thread
import random
import socket
import sys


MAX_BUFF_SIZE = 1024


def send_string(socket, string):
	
	socket.send( bytes(string, 'utf-8') )	


def receive_string(socket):

	raw_bytes = socket.recv(MAX_BUFF_SIZE)
	return raw_bytes.decode('utf-8')	


def receive_range(client_connection_socket):

	raw_range = receive_string(client_connection_socket)
	return raw_range.split(' ')


def play_game(client_connection_socket):
	
	send_string(
		client_connection_socket,
		'Welcome to the number guessing game!\nEnter the range:'
	)

	left_bound, right_bound = receive_range(client_connection_socket)

	isWin = False

	for i in range(5):

		number = random.randint(left_bound, right_bound)

		send_string(client_connection_socket, f'You have {i} attempts')

		guessed_number = receive_string(client_connection_socket)

		if guessed_number == number:
			isWin = True
			break

		if number < guessed_number:
			send_string(client_connection_socket, 'Less')
		if number > guessed_number:
			send_string(client_connection_socket, 'Greater')
		

	if isWin:
		send_string(client_connection_socket, 'You win!')
	else:
		send_string(client_connection_socket, 'You lose')




def thread_procedure(client_address, main_thread_client_con_sock):

	thread_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	thread_socket.bind((SERVER_IP, 0))

	new_thread_port = thread_socket.getsockname()[1]
	main_thread_client_con_sock.send(bytes(new_thread_port))
	main_thread_client_con_sock.close()

	try:
		thread_socket.listen()
		thread_socket.settimeout(5)
		client_connection_socket, _ = thread_socket.accept()
		play_game(client_connection_socket)
	except socket.timeout:
		return


if __name__ == '__main__':

	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	
	# getting the port number
	try:
		SERVER_PORT = sys.argv[1]
		SERVER_IP = 'localhost'
		SERVER_ADDRESS = (SERVER_PORT, SERVER_IP)
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
	clients_online = 0

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


