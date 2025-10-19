import sys
import math
from logger import logger, setup_logging
from config_parser import parse_common_config, parse_peer_info
from bitfield import Bitfield

class Peer:
    def __intit__(self, peer_id):
        # load basic config
        self.peer_id = peer_id
        self.common_config = parse_common_config('Common.cfg')
        self.peer_info = parse_peer_info('PeerInfo.cfg')

        # set up logger
        setup_logging(peer_id)
        logger.info(f"Peer {self.peer_id} starting up...")

        self.my_info = None
        for peer in self.peer_info:
            if peer['peer_id'] == self.peer_id:
                self.my_info = peer
                break
