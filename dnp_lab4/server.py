from multithreading import Thread
from multithreading import Lock
import socket
import sys


new_thread_port = None
lock = Lock()


def game(client_address):

	thread_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	thread_socket.bind((SERVER_IP, 0))

	lock.acquire()
	new_thread_port = thread_socket.getsockname()[1]
	lock.release()

	



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

		client_socket, client_address = server_socket.accept()
		clients_online += 1

		if clients_online > 2:
			client_socket.send(bytes('The server is full'))
			client_socket.close()
			continue

		print('Client connected')

		new_thread = Thread(target=game, args=(client_address,))
		new_thread.start()

		client_socket.send(bytes(new_thread_port))

		client_socket.close()


