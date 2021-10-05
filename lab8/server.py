from enum import Enum
from datetime import datetime
import sys
import random
import time

State = Enum(
    value='State',
    names=(
        'FOLLOWER',
        'CANDIDATE',
        'LEADER'
    )
)

class Server:

    other_servers = list()
    term = 0
    state = State.FOLLOWER
    not_voted = True
    
    leader_id = None
    leader_address = None


    @staticmethod
    def suspend(period):
        print(f'sleeping for {period} seconds')
        # TODO: implement sleeping


    @staticmethod
    def get_leader(self):
        return self.leader_id, self.leader_address


    def set_timer(self):

        self.timer_start_time = time.time()
        self.heartbeat_time = random.randint(150, 300) * (10 ** -3)


    def is_timer_up(self):
        return (time.time() - self.timer_start_time) > self.heartbeat_time


    def request_vote(self, term, candidate_id):
        
        if term > self.term:
            self.term = term
            self.not_voted = True

        if term == self.term and self.not_voted:
            self.state = State.FOLLOWER
            self.not_voted = False
            return self.state, True

        return self.state, False


    def append_entries(self, term, leader_id):

        self.set_timer()

        if term >= self.term:
            return self.term, True
        else:
            return self.term, False
    

    def run(self):
        pass

if __name__ == '__main__':
    
    id = sys.argv[1]

    server = Server()

    with open('config.conf') as configfile:

        for line in configfile:
            
            config_entry = line.split()

            if config_entry[0] == id:
                server_ip = config_entry[1]
                server_port = config_entry[2]
                server_address = (server_ip, server_port)
            else:
                server.other_servers.append(config_entry)
    
    print(f'server is started at {server_ip}:{server_port}')

    
