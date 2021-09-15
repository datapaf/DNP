from xmlrpc.client import ServerProxy
from registry import Registry
from node import Node
from parameters import REGISTER_IP
from parameters import REGISTER_PORT
from parameters import m
import sys
import time

if __name__ == '__main__':

	if len(sys.argv) == 4:
		m = sys.argv[1]
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
		print(f'node with port {port} created')


	with ServerProxy(f'http://{REGISTER_IP}:{REGISTER_PORT}') as register_proxy:
		for node in nodes:
			print(node.id)
			node.finger_table = register_proxy.populate_finger_table(node.id)

	while True:

		command = input().split(' ')

		if command[0] == 'get_chord_info':
			with ServerProxy(f'http://{REGISTER_IP}:{REGISTER_PORT}') as register_proxy:
				print(register_proxy.get_chord_info())
		elif command[0] == 'get_finger_table':
			with ServerProxy(f'http://{REGISTER_IP}:{command[1]}') as node_proxy:
				print(node_proxy.get_finger_table())
		else:
			print('no such command')
