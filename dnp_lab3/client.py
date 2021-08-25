import socket
import os
import time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 12345
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
FULL_FILENAME = 'innopolis.jpg'
START_SEQ_NUM = 0

sock = socket.socket(
	socket.AF_INET,
	socket.SOCK_DGRAM
)


def compose_start_message(start_seq_num, extension, size):
	return f's|{start_seq_num}|{extension}|{size}'


def compose_data_message(seq_num, data_bytes):
	return f'd|{seq_num}|{data_bytes}'


def send_string(string):
	sock.sendto(
		bytes(string, 'utf-8'),
		SERVER_ADDRESS
	)


def receive_string():
	string, addr = sock.recvfrom(1024)
	return string.decode("utf-8")


def send_start_message(extension, size, start_seq_num=START_SEQ_NUM):
	start_message = compose_start_message(
		start_seq_num,
		extension,
		size
	)

	# DEBUG
	print(time.time(), start_message, '-->')
	
	for i in range(5):
		print(f'try #{i+1} to send the start message')
		try:
			send_string(start_message)
			sock.settimeout(0.5)
			return receive_first_ack()
		except socket.timeout:
			continue

	raise Exception('The first ack was not received. Server not available.')


def receive_first_ack():
	string = receive_string()

	# DEBUG
	print(time.time(), string, '<--')

	arguments = string.split('|')

	if len(arguments) != 3:
		raise Exception('Incorrect number of arguments in the first ack') 

	next_seq_num = int(arguments[1])
	maxsize = int(arguments[2])

	return next_seq_num, maxsize


def send_data_message(seq_num, data_bytes):
	data_message = compose_data_message(
		seq_num,
		data_bytes
	)
	
	# DEBUG
	#print(time.time(), data_message, '-->')

	send_string(data_message)


def get_data_bytes(file, seq_num, maxsize):
	num_of_bytes_to_read = maxsize - len(
		bytes(compose_data_message(seq_num, ''), 'utf-8')
	)
	return file.read(num_of_bytes_to_read)


def receive_ack():
	string = receive_string()

	# DEBUG
	print(time.time(), string, '<--')

	arguments = string.split('|')

	if len(arguments) != 2:
		raise Exception('Incorrect number of arguments in the ack') 

	next_seq_num = int(arguments[1])

	return next_seq_num


def send_file(file, seq_num, maxsize):
	data_bytes = get_data_bytes(file, seq_num, maxsize)
	while len(data_bytes) != 0:

		isAckReceived = False

		for i in range(5):
			try:
				print(f'try #{i+1} to send the data chunk {seq_num}')
				send_data_message(seq_num, data_bytes)

				print(f'sent {len(data_bytes)} bytes')

				sock.settimeout(0.5)
				
				if receive_ack() != seq_num + 1:
					raise Exception('Received an incorrect ack')
				

				isAckReceived = True
				seq_num += 1
				data_bytes = get_data_bytes(file, seq_num, maxsize)
				break

			except socket.timeout:
				continue

		if not isAckReceived:
			raise Exception('The ack was not received. Server not available.')


if __name__ == "__main__":

	with open(FULL_FILENAME, 'rb') as file:
		extension = os.path.splitext(FULL_FILENAME)[1]
		size = os.path.getsize(FULL_FILENAME)
		
		seq_num, maxsize = send_start_message(extension, size)

		send_file(file, seq_num, maxsize)
