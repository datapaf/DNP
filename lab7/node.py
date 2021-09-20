from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from threading import Thread
from parameters import REGISTER_IP
from parameters import REGISTER_PORT
import time


class Node(Thread):

	def __init__(self, port):
		
		Thread.__init__(self)

		with ServerProxy(f'http://{REGISTER_IP}:{REGISTER_PORT}') as register_proxy:

			self.id, message = register_proxy.register(port)
			if self.id == -1:
				raise Exception(message)

			self.port = port
			self.server = SimpleXMLRPCServer((REGISTER_IP, port), logRequests=False)

			self.server.register_function(self.get_finger_table)
			self.server.register_function(self.quit)

			self.start()


	def run(self):

		Thread(target=self.update_finger_table_every_second).start()
		
		self.server.serve_forever()

	def update_finger_table_every_second(self):
		
		while True:

			time.sleep(1)

			with ServerProxy(f'http://{REGISTER_IP}:{REGISTER_PORT}') as register_proxy:
				self.finger_table = register_proxy.populate_finger_table(int(self.id))[0]

	def get_finger_table(self):
		return self.finger_table

	def quit(self):

		with ServerProxy(f'http://{REGISTER_IP}:{REGISTER_PORT}') as register_proxy:		
			response, message = register_proxy.deregister(self.id)

		if response == True:
			return True, 'Quit successfull'
		else:
			return False, message
