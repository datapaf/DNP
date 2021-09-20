from xmlrpc.server import SimpleXMLRPCServer
from threading import Thread
import random
from parameters import REGISTER_ADDRESS
from parameters import m


class Registry(Thread):

	def __init__(self):
		Thread.__init__(self)

		self.registered_nodes = dict()
		self.server = SimpleXMLRPCServer(REGISTER_ADDRESS, logRequests=False)

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
			new_node_id = str(new_node_id)

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

		id_list = [int(i) for i in self.registered_nodes]
		id_list.sort()

		for i in id_list:
			if i >= id:
				return i

		return id_list[0]


	def pred(self, id):

		id_list = [int(i) for i in self.registered_nodes]
		id_list.sort(reverse=True)

		for i in id_list:
			if i < id:
				return i

		return id_list[0]


	def populate_finger_table(self, id):

		finger_table = dict()

		for i in range(m):

			ith_entry = self.succ( (id + 2**i) % 2**m )

			# if ith_entry == None:
			# 	continue
			
			ith_entry = str(ith_entry)

			finger_table[ith_entry] = self.registered_nodes[ith_entry]

		pred_id = self.pred(id)
		pred_port = self.registered_nodes[str(pred_id)] 
			
		return finger_table, (pred_id, pred_port)
