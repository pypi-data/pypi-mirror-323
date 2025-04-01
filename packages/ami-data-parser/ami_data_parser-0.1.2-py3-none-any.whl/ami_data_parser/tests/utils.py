from ami_data_parser.entities.peer import Peer


class PeerTest(Peer):

    def _get_timestamp(self):
        return 1736960329.736009
    

def get_peers_test(data: list) -> list:
    return [
        PeerTest(**item)
        for item in data
    ]