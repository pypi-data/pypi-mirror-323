from ami_data_parser.entities.queue import Queue
from ami_data_parser.factories.peer_factory import get_peers
from ami_data_parser.factories.queue_factory import get_queues
from ami_data_parser.parser.hint_parser import HintParser
from ami_data_parser.parser.queue_parser import QueueParser
from ami_data_parser.repositories.peer_repository import PeerRepository
from ami_data_parser.repositories.queue_repository import QueueRepository


class Controller:

    def __init__(self):
        self._hint_parser = HintParser()
        self._queue_parser = QueueParser()
        self._peer_repository = PeerRepository()
        self._queue_repository = QueueRepository()
        self._queues_members_dict = {}
        self._get_peers = get_peers
        self._get_queues = get_queues

    def get(self, entity_key: str, entity_type: str, raise_exception=False):

        if entity_type == 'peer':

            if not self._peer_repository.exists(entity_key) and not raise_exception:
                return None
            
            return self._peer_repository.get(entity_key)
        
        elif entity_type == 'queue':

            if not self._queue_repository.exists(entity_key) and not raise_exception:
                return None
            
            return self._queue_repository.get(entity_key)
        
        raise TypeError(f'Invalid type: {entity_type}')

    def get_list_queues_from_a_peer(self, key: str) -> list:
        return self._queues_members_dict.get(key, [])

    def peer_update(self, received_data: list) -> list:
        data = []
        parser_data = self._hint_parser.get_data(received_data)
        peers_data = self._get_peers(parser_data)
        self._peer_repository.set(
            peers_data
        )
        peers_diff = self._peer_repository.diff()

        for peer, event in peers_diff:
            
            if event == 'removed':
                peer_dict = {'peername': peer, 'type': 'peer'}
            
            else:
                peer_dict = vars(self._peer_repository.get(peer))
            
            peer_dict['event'] = event
            data.append(peer_dict)
        
            
        return data

    def queue_update(self, received_data: list) -> list:
        data = []
        parser_data = self._queue_parser.get_data(received_data)
        self.set_list_queues_from_members(parser_data)
        queues_data = self._get_queues(parser_data)
        self._queue_repository.set(
            queues_data
        )
        queues_diff = self._queue_repository.diff()

        for queue, event in queues_diff:

            if event == 'removed':
                queue_dict = {'queuename': queue, 'type': 'queue'}
            
            else:
                queue_data: Queue = self._queue_repository.get(queue)
                queue_dict = queue_data.get_dict()

            queue_dict['event'] = event
            data.append(queue_dict)
        
        return data
    
    def set_list_queues_from_members(self, parser_data: list):
        self._clear_queues_members_dict()

        for queue_data in parser_data:
            queuename = queue_data.get('queuename')

            for member_data in queue_data.get('members', []):
                membername = member_data.get('name')

                if membername not in self._queues_members_dict:
                    self._queues_members_dict[membername] = []
                
                if queuename not in self._queues_members_dict[membername]:
                    self._queues_members_dict[membername].append(queuename)              
    
    def _clear_queues_members_dict(self):
        self._queues_members_dict = {}