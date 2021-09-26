from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from threading import Thread
import params
import time
import zlib

def rotate_list(l, n):
	return l[n:] + l[:n]

class Node(Thread):

	def __init__(self, port):
		
		Thread.__init__(self)

		with ServerProxy(f'http://{params.REGISTER_IP}:{params.REGISTER_PORT}') as register_proxy:

			self.id, message = register_proxy.register(port)
			if self.id == -1:
				raise Exception(message)

			self.filenames = list()

			self.port = port
			self.server = SimpleXMLRPCServer((params.REGISTER_IP, port), logRequests=False)

			self.server.register_function(self.get_finger_table)
			self.server.register_function(self.quit)
			self.server.register_function(self.return_filenames)
			self.server.register_function(self.add_filename)
			self.server.register_function(self.savefile)

			self.start()

			self.ft_updater = Thread(target=self.update_finger_table_every_second)
			self.ft_updater.start()

	def run(self):
		
		self.server.serve_forever()

	def update_finger_table_every_second(self):
		
		while True:

			time.sleep(1)

			with ServerProxy(f'http://{params.REGISTER_IP}:{params.REGISTER_PORT}') as register_proxy:
				self.finger_table = register_proxy.populate_finger_table(int(self.id))[0]

	def return_filenames(self):
		return self.filenames

	def add_filename(self, filename):
		try:
			self.filenames.append(filename)
			return True
		except:
			raise Exception('cannot add filename')


	def get_finger_table(self):
		return self.finger_table

	def quit(self):

		with ServerProxy(f'http://{params.REGISTER_IP}:{params.REGISTER_PORT}') as register_proxy:	
			response, message = register_proxy.deregister(self.id)

		self.ft_updater._stop.set()

		if response == True:
			return True, 'Quit successfull'
		else:
			return False, message

	def lookup(self, target_id):

		with ServerProxy(f'http://{params.REGISTER_IP}:{params.REGISTER_PORT}') as register_proxy:

			if register_proxy.pred(self.id) < target_id and target_id <= self.id:
				
				return self.id

			elif self.id < target_id and target_id <= register_proxy.succ(self.id, False):
				
				finger_table_nodes = [int(node) for node in self.finger_table.keys()]
				finger_table_nodes.sort()
				
				for node in finger_table_nodes:
					if node > self.id:
						return node

				raise Exception('Node to save not found 1')

			else:

				finger_table_nodes = [int(node) for node in self.finger_table.keys()]
				finger_table_nodes.sort()

				rotations = 0
				while not finger_table_nodes[0] > self.id:
				    finger_table_nodes = rotate_list(finger_table_nodes, 1)
				    rotations += 1

				for i in range(len(finger_table_nodes)):
				    if i >= rotations and finger_table_nodes[i] > target_id:
				        return finger_table_nodes[i-1]

				raise Exception('Node to save not found 2')

	def savefile(self, filename):

		hash_value = int(zlib.adler32(filename.encode()))
		target_id = hash_value % 2 ** params.m

		node_to_save_id = self.lookup(target_id)
		
		if node_to_save_id == self.id:

			node_to_save_port = self.port
			
			if filename in self.filenames:
				return False, f"Filename already exists in Node {node_to_save_id}"

			self.add_filename(filename)

			return True, f"filename is saved in Node {node_to_save_id}"			

		else:

			print(f'node {self.id} passed {filename} to node {node_to_save_id}')

			node_to_save_port = self.finger_table[str(node_to_save_id)]

			with ServerProxy(f'http://{params.REGISTER_IP}:{node_to_save_port}') as node_proxy:

				# filenames = node_proxy.return_filenames()

				# if filename in filenames:
				# 	return False, f"Filename already exists in Node {node_to_save_id}"

				# node_proxy.add_filename(filename)

				# return True, f"filename is saved in Node {node_to_save_id}"

				return node_proxy.savefile(filename)
