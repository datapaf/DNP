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

class Timer(Thread):
    
    def __init__(self):
        Thread.__init__(self)
        self.waiting_time = None
        self.is_up = False

    
    def set(self, time):
        self.waiting_time = time
        self.is_up = False


    def wait(self):
        
        timing = datetime.datetime.now()
        
        while True:
            if (datetime.datetime.now() - timing).total_seconds() * 1000 > self.waiting_time:
                break


    def run(self):

        while True:
            if not self.is_up and self.waiting_time != None:
                self.wait()
                self.is_up = True

class RPCServer(Thread):

    def __init__(self, node):
        Thread.__init__(self)
        
        self.server = SimpleXMLRPCServer(node.my_address)
        self.server.register_function(node.suspend)
        self.server.register_function(node.get_leader)
        self.server.register_function(node.request_vote)
        self.server.register_function(node.append_entries)

    def run(self):
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

        self.timer = Timer()
        self.rpc = RPCServer(self)

        self.sleep_for = 0
    

    def suspend(self, period):
        print(f'Command from client: suspend {period}')
        print(f'sleeping for {period} seconds')
        self.sleep_for = period


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
            self.state = State.FOLLOWER
            self.not_voted = False
            return self.term, True

        return self.term, False


    def append_entries(self, term, leader_id):

        self.timer.set(random.randint(150, 300))

        if term >= self.term:
            return self.term, True
        else:
            return self.term, False


    def change_state(self, new_state, msg=None):

        if self.state == State.FOLLOWER and new_state == State.CANDIDATE:
            self.term += 1
            self.timer.set(random.randint(150, 300))

        elif self.state == State.CANDIDATE and new_state == State.FOLLOWER:

            if msg != None and msg[0] == 'vote with higher term':
                self.term = msg[1]

            self.timer.set(random.randint(150, 300))

        elif self.state == State.CANDIDATE and new_state == State.LEADER:
            RAFTNode.leader_id = self.id
            RAFTNode.leader_address = self.my_address

        self.state = new_state
        self.is_state_shown = False


    def show_state_and_term(self):
        if not self.is_state_shown:
            print(f'I am a {self.state.value}. Term: {self.term}')
            self.is_state_shown = True


    def run(self):

        self.rpc.start()
        print(f'server started at {self.my_address[0]}:{self.my_address[1]}')

        self.timer.start()
        self.timer.set(random.randint(150, 300))

        while True:

            self.show_state_and_term()

            if self.sleep_for > 0:
                time.sleep(self.sleep_for)

            if self.state == State.FOLLOWER:

                if self.timer.is_up:
                    print('The leader is dead')
                    self.change_state(State.CANDIDATE)

            elif self.state == State.CANDIDATE:
                
                if self.not_voted:
                    
                    votes = 0
                    n_voters = 0

                    for id in self.addresses:
                        
                        if id == self.id:
                        
                            n_voters += 1
                            
                            votes += 1
                            self.not_voted = False
                            print(f'Voted for node {id}')
                            print('Votes received')
                        
                        else:
                            
                            try:

                                with ServerProxy(f'http://{self.addresses[id][0]}:{self.addresses[id][1]}') as other_node:

                                    response = other_node.request_vote(self.term, self.id)
                                    n_voters += 1

                                    if response[0] > self.term:
                                        self.change_state(
                                            State.FOLLOWER, 
                                            ('vote with higher term', response[0])
                                        )
                                        break
                                    
                                    if response[1] == True:
                                        votes += 1
                                        print('Votes received')
                            
                            except ConnectionRefusedError:
                                continue

                    # voting stopped due to vote with higher term
                    if self.state == State.FOLLOWER:
                        continue

                    if votes > n_voters / 2 and not self.timer.is_up:
                        self.change_state(State.LEADER)
                    else:
                        self.change_state(State.FOLLOWER)
                
            elif self.state == State.LEADER:
                pass


if __name__ == '__main__':
    
    id = sys.argv[1]

    with open('config.conf') as configfile:

        addresses = dict()

        for line in configfile:
            config_entry = line.split()
            addresses[config_entry[0]] = (config_entry[1], int(config_entry[2]))

    node = RAFTNode(id, addresses)
    node.run()
