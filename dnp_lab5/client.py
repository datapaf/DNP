from xmlrpc.client import ServerProxy
import sys
import os


def print_response(response):

	if response == True:
		print('Completed')
	else:
		print('Not completed')


if __name__ == '__main__':

	SERVER_IP = sys.argv[1]
	SERVER_PORT = int(sys.argv[2])
	SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)

	try:

		with ServerProxy(f'http://{SERVER_IP}:{SERVER_PORT}') as proxy:
		
			while True:

				print('\nEnter the command:')
				command = input().split(' ')
				operation = command[0]

				if operation == 'quit':
					
					print('Client is stopping')
					sys.exit(0)
				
				elif operation == 'send':

					filename = command[1]
					
					if not os.path.isfile(filename):
						print(f'No such file')
						continue

					with open(filename, 'rb') as file:
						data = file.read()
						response = proxy.send_file(filename, data)
						print_response(response)

				elif operation == 'list':

					filenames = proxy.list_files()

					for filename in filenames:
						print(filename)

				elif operation == 'delete':

					filename = command[1]

					response = proxy.delete_file(filename)
					print_response(response)

				elif operation == 'get':

					if len(command) == 3:
						filename = command[1]
						new_filename = command[2]
						filename_to_open = new_filename
					else:
						filename = command[1]
						filename_to_open = filename

					if os.path.isfile(filename_to_open):
						print(f'File already exists')
						continue

					with open(filename_to_open, 'wb') as file:
							data = proxy.get_file(filename)
							file.write(data)

				elif operation == 'calc':

					expression = f'{command[1]} {command[2]} {command[3]}'

					print(proxy.calculate(expression))


	except KeyboardInterrupt:

		print('Client is stopping')
		sys.exit(0)
