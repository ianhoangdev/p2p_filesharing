import sys
import math
import socket
import threading
from logger import logger, setup_logging
from config_parser import parse_common_config, parse_peer_info
from bitfield import Bitfield
from connection import ConnectionHandler

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
        for p_info in self.peer_info:
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
        
        server_thread = threading.Thread(target=self._start_server)
        server_thread.daemon = True
        server_thread.start()

        self._connect_to_peers()

        try:
            while True:
                ...
                pass
        except KeyboardInterrupt:
            logger.info(f"Peer {self.peer_id} shutting down.")

    def _start_server(self):
        # Listens for incoming connections from other peers. Runs in its own thread.
        try:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((self.host, self.port))
            server_socket.listen(len(self.peer_info)) # how many peers can we listen to at once
            
            logger.info(f"Server started. Listening on {self.host}:{self.port}")
            
            while True:
                # Accept a new connection
                client_sock, client_addr = server_socket.accept()
                logger.info(f"Accepted connection from {client_addr}")
                
                # Create a new handler thread for this connection
                # We don't know the peer_id yet; handshake will determine it.
                handler = ConnectionHandler(client_sock, self)
                handler.start()
                
        except Exception as e:
            logger.error(f"Server thread crashed: {e}", exc_info=True)

    def _connect_to_peers(self):
        # connects to all peers listed before
        # Find the index of this peer
        my_index = next(i for i, p in enumerate(self.peer_info) 
                        if p['peer_id'] == self.peer_id)
        
        # Iterate only over peers before this one
        for i in range(my_index):
            remote_peer_info = self.peer_info[i]
            remote_peer_id = remote_peer_info['peer_id']
            host = remote_peer_info['host_name']
            port = remote_peer_info['port']
            
            try:
                # Create a new socket to connect to the other peer
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((host, port))
                
                # Log the "makes a connection to" message
                logger.info(f"Peer {self.peer_id} makes a connection to Peer {remote_peer_id}.")
                
                # Create a handler thread for this *outgoing* connection
                # This time, we *do* know the peer_id we are connecting to.
                handler = ConnectionHandler(client_socket, self, remote_peer_id)
                handler.start()

            except ConnectionRefusedError:
                logger.warning(f"Connection refused by {remote_peer_id} at {host}:{port}. Is it running?")
            except Exception as e:
                logger.error(f"Failed to connect to {remote_peer_id}: {e}", exc_info=True)