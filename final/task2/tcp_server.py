from threading import Thread
import socket
import hash

SERVER_IP = '127.0.0.1'
SERVER_PORT = 50505
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
MAX_BUFF_SIZE = 1024


def send_string(socket, string):
	
	socket.send( bytes(string, 'utf-8') )	


def receive_string(socket):

	raw_bytes = socket.recv(MAX_BUFF_SIZE)
	return raw_bytes.decode('utf-8')


def thread_procedure(conn):

    try:
        while True:
            string = receive_string(conn)
            print(f'Message: {string}')
            send_string(conn, hash.calc_hash(string))
    except:
        print('Client disconnected')
        conn.close()


if __name__ == "__main__":
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind(SERVER_ADDRESS)

    print(f'Server is running on {SERVER_ADDRESS}')

    server_socket.listen()

    try:
        while True:

            conn, _ = server_socket.accept()

            new_thread = Thread(target=thread_procedure, args=(conn, ))
            new_thread.start()
    
    except KeyboardInterrupt:
        print('Server is stopped')
        server_socket.close()
