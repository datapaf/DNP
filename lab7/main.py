from xmlrpc.client import ServerProxy
from registry import Registry
from node import Node
import params
import zlib
import sys
import time


if __name__ == '__main__':

	if len(sys.argv) == 4:
		params.m = int(sys.argv[1])
		first_port = int(sys.argv[2])
		last_port = int(sys.argv[3])
	elif len(sys.argv) == 3:
		first_port = int(sys.argv[1])
		last_port = int(sys.argv[2])
	else:
		raise Exception('Incorrect number of arguments')

	register = Registry()
	print('register created')

	nodes = []

	for port in range(first_port, last_port + 1):
		nodes.append(Node(port))

	print(f'{len(nodes)} nodes created')

	while True:

		command = input().split(' ')

		if command[0] == 'get_chord_info':
		
			with ServerProxy(f'http://{params.REGISTER_IP}:{params.REGISTER_PORT}') as register_proxy:
				print(register_proxy.get_chord_info())
		
		elif command[0] == 'get_finger_table':
		
			with ServerProxy(f'http://{params.REGISTER_IP}:{command[1]}') as node_proxy:
				print(node_proxy.get_finger_table())
		
		elif command[0] == 'save':

			filename = command[2]
			hash_value = zlib.adler32(filename.encode())
			target_id = hash_value % 2 ** params.m
			print(f"{filename} has identifier {target_id}")
			
			with ServerProxy(f'http://{params.REGISTER_IP}:{command[1]}') as node_proxy:
				response = node_proxy.savefile(filename)

			print(response)

		elif command[0] == 'quit':
		
			with ServerProxy(f'http://{params.REGISTER_IP}:{command[1]}') as node_proxy:
				response, message = node_proxy.quit()
		
			print(message)
		
		else:
			print('no such command')
