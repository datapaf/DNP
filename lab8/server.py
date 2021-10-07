import threading
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from threading import Thread
import datetime
from enum import Enum
import sys
import random
import time

class State(Enum):
    FOLLOWER = 'follower'
    CANDIDATE = 'candidate'
    LEADER = 'leader'

def wait_for(time_ms):
    timing = datetime.datetime.now()
    while True:
        if (datetime.datetime.now() - timing).total_seconds() * 1000 > time_ms:
            break

class Timer(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.is_up = threading.Event()


    def set(self, time_ms): 
        self.is_up.clear()
        self.deadline = int(time.time() * 1000) + time_ms
        

    def run(self):
        while True:
            if not self.is_up.is_set() and int(time.time() * 1000) > self.deadline:
                self.is_up.set()

class RPCServer(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        
        self.server = SimpleXMLRPCServer(node.my_address, logRequests=False)
        self.server.register_function(node.suspend)
        self.server.register_function(node.get_leader)
        self.server.register_function(node.request_vote)
        self.server.register_function(node.append_entries)

    def run(self):
        print(f'server started at {self.server.server_address[0]}:{self.server.server_address[1]}')
        self.server.serve_forever()

class RAFTNode:

    leader_id = None
    leader_address = None

    def __init__(self, id, addresses):
        
        self.id = id
        self.addresses = addresses
        self.my_address = (addresses[id][0], addresses[id][1])

        self.term = 0

        self.is_state_shown = False
        self.state = State.FOLLOWER
        
        self.not_voted = True

        self.rpc = RPCServer(self)
        self.timer = Timer()

        self.sleep_for = 0
    

    def suspend(self, period):
        print(f'Command from client: suspend {period}')
        print(f'sleeping for {period} seconds')
        self.sleep_for = int(period)
        return True


    def get_leader(self):
        print('Command from client: getleader')
        print(f'{self.leader_id} {self.leader_address[0]}:{self.leader_address[1]}')
        return self.leader_id, self.leader_address


    def request_vote(self, term, candidate_id):

        self.timer.set(random.randint(150, 300))

        if term > self.term:
            self.term = term
            self.not_voted = True

        if term == self.term and self.not_voted:
            self.not_voted = False
            print(f'voted for node {candidate_id}')
            return self.term, True
        
        return self.term, False


    def append_entries(self, term, leader_id):

        self.timer.set(random.randint(150, 300))

        if term >= self.term:
            return self.term, True
    
        return self.term, False


    def change_state(self, new_state, new_term=None):

        self.timer.set(random.randint(150, 300))

        if self.state == State.FOLLOWER and new_state == State.CANDIDATE:
            self.term += 1

        elif self.state == State.CANDIDATE and new_state == State.FOLLOWER:

            if new_term != None:
                self.term = new_term

        elif self.state == State.CANDIDATE and new_state == State.LEADER:
            RAFTNode.leader_id = self.id
            RAFTNode.leader_address = self.my_address

        elif self.state == State.LEADER and new_state == State.FOLLOWER:
            self.term = new_term

        self.state = new_state
        self.is_state_shown = False


    def show_state_and_term(self):
        if not self.is_state_shown:
            print(f'I am a {self.state.value}. Term: {self.term}')
            self.is_state_shown = True


    def run(self):

        self.rpc.start()

        self.timer.set(random.randint(150, 300))
        self.timer.start()

        while True:

            # print state and term if the state has been changed
            self.show_state_and_term()

            # sleep if suspend is called
            if self.sleep_for > 0:
                time.sleep(self.sleep_for)
                self.sleep_for = 0
                print('woke up')

            if self.state == State.FOLLOWER:

                self.timer.is_up.wait()

                print('The leader is dead')
                self.change_state(State.CANDIDATE)

            elif self.state == State.CANDIDATE:
                
                if self.not_voted:
                    
                    votes = 0
                    n_voters = 0

                    for id in self.addresses:
                        
                        try:
                            
                            with ServerProxy(f'http://{self.addresses[id][0]}:{self.addresses[id][1]}') as other_node:
                                
                                response = other_node.request_vote(self.term, self.id)
                                n_voters += 1

                                if response[0] > self.term:
                                    self.change_state(State.FOLLOWER, new_term=response[0])
                                    # stop voting due to vote with higher term
                                    break
                                    
                                if response[1] == True:
                                    votes += 1
                                    print('Votes received')
                            
                        except ConnectionRefusedError:
                            continue

                    # voting stopped due to vote with higher term
                    if self.state == State.FOLLOWER:
                        continue
                    
                    if votes > n_voters / 2 and not self.timer.is_up.is_set():
                        self.change_state(State.LEADER)
                    else:
                        print('here')
                        self.change_state(State.FOLLOWER)
            
            if self.state == State.LEADER:

                time.sleep(0.05)

                for id in self.addresses:

                    try:
                        with ServerProxy(f'http://{self.addresses[id][0]}:{self.addresses[id][1]}') as other_node:
                            response = other_node.append_entries(self.term, self.id)
                            if response[0] > self.term:
                                self.change_state(State.FOLLOWER, new_term=response[0])
                                break
                    except ConnectionRefusedError:
                        continue

if __name__ == '__main__':
    
    id = sys.argv[1]

    with open('config.conf') as configfile:

        addresses = dict()

        for line in configfile:
            config_entry = line.split()
            addresses[config_entry[0]] = (config_entry[1], int(config_entry[2]))

    node = RAFTNode(id, addresses)
    node.run()
