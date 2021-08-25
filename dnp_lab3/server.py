from threading import Thread
from threading import Lock
import socket
import time

SERVER_IP = '127.0.0.1'
SERVER_PORT = 12345
SERVER_ADDRESS = (SERVER_IP, SERVER_PORT)
BUFFER_SIZE = 1024

receiving_sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)
receiving_sock.bind(SERVER_ADDRESS)

sending_sock = socket.socket(
    socket.AF_INET,
    socket.SOCK_DGRAM
)

lock = Lock()

class Session:

    def __init__(self, next_seq_num, last_reception_tstamp, extension, size):
        self.chunks = dict()
        self.next_seq_num = next_seq_num
        self.last_reception_tstamp = last_reception_tstamp
        self.extension = extension
        self.size = size
        self.isFileReceptionFinished = False


    def get_all_chunks_size(self):
        all_chunks_size = 0
        for seq_num in self.chunks:
            all_chunks_size += len(self.chunks[seq_num])
        return all_chunks_size


    def __str__(self):
        return f'''
            chunks: {self.chunks.keys()}
            all_chunks_size: {self.get_all_chunks_size()}
            next_seq_num: {self.next_seq_num}
            last_reception_tstamp: {self.last_reception_tstamp}
            extension: {self.extension}
            size: {self.size}
        '''


def send_string(string, address):
    sending_sock.sendto(
        bytes(string, 'utf-8'),
        address
    )


def receive_string():
    data, addr = receiving_sock.recvfrom(BUFFER_SIZE)
    return data.decode("utf-8"), addr


def find_second_divider(string):
   return string.find('|', string.find('|') + 1)


def receive_and_unpack_message():
    raw_message, address = receive_string()
    
    if raw_message[0] == 's':
        return raw_message.split('|'), address

    second_divider_index = find_second_divider(raw_message)

    message = raw_message[:second_divider_index].split('|')
    message.append(raw_message[second_divider_index+1:])

    return message, address


def compose_starting_ack(next_seq_num, maxsize):
    return f'a|{next_seq_num}|{maxsize}'


def compose_ack(next_seq_num):
    return f'a|{next_seq_num}'


def send_starting_ack(next_seq_num, maxsize, address):
    starting_ack = compose_starting_ack(
        next_seq_num,
        maxsize
    )

    # DEBUG
    print(time.time(), starting_ack, '-->')

    send_string(starting_ack, address)


def send_ack(next_seq_num, address):
    ack = compose_ack(next_seq_num)

    # DEBUG
    print(time.time(), ack, '-->')

    send_string(ack, address)


def process_sessions(sessions):
    while True:
            
        message, address = receive_and_unpack_message()

        if message[0] == 's':

            next_seq_num = int(message[1]) + 1
            extension = message[2]
            size = int(message[3])

            lock.acquire()

            sessions[address] = Session(next_seq_num, time.time(), extension, size)

            lock.release()

            send_starting_ack(next_seq_num, BUFFER_SIZE, address)

        elif message[0] == 'd':

            seq_num = int(message[1])
            next_seq_num = seq_num + 1
            data_chunk = bytes(message[2], 'utf-8')

            num_of_bytes_received = len(data_chunk) 
            print(f'received {num_of_bytes_received} bytes')

            # this consitions allows discarding duplicates
            if next_seq_num != sessions[address].next_seq_num:
                
                lock.acquire()

                sessions[address].next_seq_num = next_seq_num
                sessions[address].last_reception_tstamp = time.time()
                sessions[address].chunks[seq_num] = data_chunk

                if sessions[address].get_all_chunks_size() >= sessions[address].size:

                    sessions[address].isFileReceptionFinished = True
                    print('FILE RECEPTION DONE') # DEBUG

                lock.release()

            send_ack(next_seq_num, address)


def delete_session(sessions, address):
    lock.acquire()
    del sessions[address]
    print(f'SESSION {address} DELETED') # DEBUG
    lock.release()    


def close_lost_and_finished_sessions(sessions):
    while True:
        
        for address in list(sessions):

            time_inactive = time.time() - sessions[address].last_reception_tstamp

            if sessions[address].isFileReceptionFinished:
                if time_inactive >= 1:
                    delete_session(sessions, address)
                    break
            else:
                if time_inactive >= 3:
                    delete_session(sessions, address)
                    break   


def display_sessions(sessions):
    while True:
        time.sleep(0.5)

        if len(sessions) == 0:
            print('No saved sessions')
        else:
            print('Saved sessions:')
            for address in sessions:
                print(time.time())
                print(address, sessions[address])


if __name__ == "__main__":

    from threading import Thread

    sessions = dict()

    processing_thread = Thread(target=process_sessions, args=(sessions,))
    closing_thread = Thread(target=close_lost_and_finished_sessions, args=(sessions,))
    displaying_thread = Thread(target=display_sessions, args=(sessions,))

    processing_thread.start()
    closing_thread.start()
    displaying_thread.start()

    processing_thread.join()
    closing_thread.join()
    displaying_thread.join()

    processing_thread.close()
    closing_thread.close()
    displaying_thread.close()
