from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
import random
from parameters import REGISTER_ADDRESS
from parameters import m


class Registry(Thread):

	def __init__(self):
		Thread.__init__(self)

		self.registered_nodes = dict()
		self.server = SimpleXMLRPCServer(REGISTER_ADDRESS)

		self.server.register_function(self.register)
		self.server.register_function(self.deregister)
		self.server.register_function(self.get_chord_info)
		self.server.register_function(self.populate_finger_table)

		self.start()

	def run(self):
		self.server.serve_forever()

	def register(self, port):
		
		random.seed(0)

		if len(self.registered_nodes) == 2**m:
			return -1, 'Unable to register: the Chord is full'

		while True:
			new_node_id = random.randint(0, 2**m - 1)
			if new_node_id not in self.registered_nodes:
				break

		self.registered_nodes[new_node_id] = port

		return new_node_id, len(self.registered_nodes)

	def deregister(self, id):

		try:
			del self.registered_nodes[id]
		except KeyError:
			return False, 'Unable to deregister: No such id'
		except:
			return False, 'Unable to deregister: Unknown error'

		return True, 'Deregistered successfully'

	def get_chord_info(self):
		
		return self.registered_nodes 

	def succ(self, id):

		id_list = list(self.registered_nodes.keys())
		id_list.sort()

		for i in id_list:
			if i > id:
				return i

	def populate_finger_table(self, id):

		finger_table = dict()

		for i in range(1, m + 1):
			ith_entry = self.succ(id + 2**(i-1))
			finger_table[ith_entry] = self.registered_nodes[ith_entry]
			print(f'finger_table[{ith_entry}] =', finger_table[ith_entry])
			# finger_table[i] = succ(id + 2**(i-1))

		return finger_table
