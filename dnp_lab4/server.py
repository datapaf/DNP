import socket
import sys

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if __name__ == '__main__':
	
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

		



