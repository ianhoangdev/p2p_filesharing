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
        
        # initialize peer attributes
        self.host = self.my_info['host_name']
        self.port = self.my_info['port']
        self.has_file = self.my_info['has_file']

        logger.info(f"My info: Host={self.host}, Port={self.port}, HasFile={self.has_file}")

        # file and piece size
        self.file_size = self.common_cfg['FileSize']
        self.piece_size = self.common_cfg['PieceSize']
        
        self.bitfield = Bitfield(self.file_size, self.piece_size, self.has_file)
        self.total_pieces = self.bitfield.total_pieces

        logger.info(f"File: {self.common_cfg['FileName']}, Size: {self.file_size} bytes")
        logger.info(f"Total pieces: {self.total_pieces}, Piece size: {self.piece_size} bytes")
        if self.has_file:
            logger.info("I am a 'seed' (I have the complete file).")

        self.neighbors = {}
        for p_info in self.peer_info_list:
            if p_info['peer_id'] != self.peer_id:
                self.neighbors[p_info['peer_id']] = {
                    'host': p_info['host_name'],
                    'port': p_info['port'],
                    'has_file_initially': p_info['has_file'],
                    'bitfield': Bitfield(self.file_size, self.piece_size, p_info['has_file']),
                    'am_choking': True,       # am I choking this neighbor?
                    'is_choking_me': True,    # is this neighbor choking me?
                    'me_interested': False,   # am I interested in their pieces?
                    'them_interested': False,   # are they interested in my pieces?
                    'socket': None,           # will hold the socket object
                    'handler_thread': None    # will hold the connection thread
                }
        
        logger.info(f"Initialized state for {len(self.neighbors)} neighbors.")

    def run(self):
        logger.info("Peer run() method called.")