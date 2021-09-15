from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from threading import Thread
from parameters import REGISTER_IP
from parameters import REGISTER_PORT


class Node(Thread):

	def __init__(self, port):
		Thread.__init__(self)

		with ServerProxy(f'http://{REGISTER_IP}:{REGISTER_PORT}') as register_proxy:

			self.id, message = register_proxy.register(port)
			if self.id == -1:
				raise Exception(message)

			self.finger_table = None
			#self.finger_table = register_proxy.populate_finger_table(self.id)


		self.port = port
		self.server = SimpleXMLRPCServer((REGISTER_IP, port))

		self.server.register_function(self.get_finger_table)
		self.server.register_function(self.quit)

		self.start()

	def run(self):
		self.server.serve_forever()

	def get_finger_table(self):
		return self.finger_table

	def quit(self):

		with ServerProxy(f'http://{REGISTER_IP}:{REGISTER_PORT}') as register_proxy:		

			response, message = register_proxy.deregister(self.id)

			self.terminate()

			if response == True:
				return True, 'Quit successfull'
			else:
				return False, message
