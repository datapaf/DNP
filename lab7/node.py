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
			self.server.register_function(self.getfile)
			self.server.register_function(self.set_successor)
			self.server.register_function(self.set_predecessor)

			self.start()

			self.updater_running = True
			self.ft_updater = Thread(target=self.update_finger_table_every_second)
			self.ft_updater.start()

	def run(self):
		
		self.server.serve_forever()

	def update_finger_table_every_second(self):
		
		while self.updater_running:

			time.sleep(1)

			with ServerProxy(f'http://{params.REGISTER_IP}:{params.REGISTER_PORT}') as register_proxy:
				self.finger_table = register_proxy.populate_finger_table(int(self.id))[0]
				
				self.predecessor = register_proxy.pred(self.id)
				self.predecessor_port = register_proxy.pred_port(self.id)
				
				self.successor = register_proxy.succ(self.id, False)
				self.successor_port = register_proxy.succ_port(self.id, False)

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

	def set_successor(self, id, port):
		try:
			self.successor = id
			self.successor_port = port
			return True
		except:
			raise Exception('cannot set successor')

	def set_predecessor(self, id, port):
		try:
			self.predecessor = id
			self.predecessor_port = port
			return True
		except:
			raise Exception('cannot set predecessor')

	def quit(self):

		with ServerProxy(f'http://{params.REGISTER_IP}:{self.predecessor_port}') as predecessor_proxy:
			with ServerProxy(f'http://{params.REGISTER_IP}:{self.successor_port}') as successor_proxy:
				successor_proxy.set_predecessor(self.predecessor, self.predecessor_port)
				predecessor_proxy.set_successor(self.successor, self.successor_port)

				for filename in self.filenames:
					successor_proxy.add_filename(filename)

		self.updater_running = False

		with ServerProxy(f'http://{params.REGISTER_IP}:{params.REGISTER_PORT}') as register_proxy:
			response, message = register_proxy.deregister(str(self.id))

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
				return node_proxy.savefile(filename)

	def getfile(self, filename):

		hash_value = int(zlib.adler32(filename.encode()))
		target_id = hash_value % 2 ** params.m

		node_to_save_id = self.lookup(target_id)
		
		if node_to_save_id == self.id:

			node_to_save_port = self.port
			
			if filename in self.filenames:
				return True, f"Node {node_to_save_id} has filename"

			return False, f"Node {node_to_save_id} doesn't have the filename"			

		else:

			print(f'node {self.id} passed {filename} to node {node_to_save_id}')

			node_to_save_port = self.finger_table[str(node_to_save_id)]

			with ServerProxy(f'http://{params.REGISTER_IP}:{node_to_save_port}') as node_proxy:
				return node_proxy.getfile(filename)		
