import datetime
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from threading import Thread

from enum import Enum
import sys
import random

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

class Server(Thread):

    def __init__(self, id, addresses):
        Thread.__init__(self)

    

class RAFTNode(Thread):

    leader_id = None
    leader_address = None


    def __init__(self, id, addresses):
        Thread.__init__(self)

        self.id = id
        self.addresses = addresses
        self.my_address = (addresses[id][0], addresses[id][1])
        
        self.server = SimpleXMLRPCServer(self.my_address)
        self.server.register_function(self.suspend)
        self.server.register_function(self.get_leader)
        self.server.register_function(self.request_vote)
        self.server.register_function(self.append_entries)
        
        self.term = 0

        self.is_state_shown = False
        self.state = State.FOLLOWER
        
        self.not_voted = True

        self.timer = Timer()
        self.timer.start()


    def suspend(period):
        print(f'sleeping for {period} seconds')
        # TODO: implement sleeping


    def get_leader(self):
        return self.leader_id, self.leader_address


    def request_vote(self, term, candidate_id):

        self.timer.set(random.randint(150, 300))

        if term > self.term:
            self.term = term
            self.not_voted = True

        if term == self.term and self.not_voted:
            self.state = State.FOLLOWER
            self.not_voted = False
            return self.state, True

        return self.state, False


    def append_entries(self, term, leader_id):

        self.timer.set(random.randint(150, 300))

        if term >= self.term:
            return self.term, True
        else:
            return self.term, False
    

    def change_state_and_term(self, new_state):

        if self.state == State.FOLLOWER and new_state == State.CANDIDATE:
            self.term += 1
            self.votes = 0
            self.timer.set(random.randint(150, 300))

        self.state = new_state
        self.is_state_shown = False


    def show_state_and_term(self):
        if not self.is_state_shown:
            print(f'I am a {self.state.value}. Term: {self.term}')
            self.is_state_shown = True


    def run(self):

        print(f'server started at {self.addresses[self.id][0]}:{self.addresses[self.id][1]}')

        self.timer.set(random.randint(150, 300))

        while True:

            self.show_state_and_term()

            if self.state == State.FOLLOWER:

                if self.timer.is_up:
                    print('The leader is dead')
                    self.change_state_and_term(State.CANDIDATE)

            elif self.state == State.CANDIDATE:
                
                if self.not_voted:
                    for id in self.addresses:
                        if id == self.id:
                            print(f'Voted for node {id}')
                            self.votes += 1
                            self.not_voted = False
                        # else:
                        #     with ServerProxy(f'http://{self.addresses[id][0]}:{self.addresses[id][1]}') as node:
                        #         node.request_vote(self.term, self.id)
                
            elif self.state == State.LEADER:
                pass


if __name__ == '__main__':
    
    id = sys.argv[1]

    with open('config.conf') as configfile:

        addresses = dict()

        for line in configfile:
            config_entry = line.split()
            addresses[config_entry[0]] = (config_entry[1], config_entry[2])

    node = RAFTNode(id, addresses)

    node.run()
