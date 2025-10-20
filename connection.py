import socket
import threading
import struct
from logger import logger
from message import (
    create_handshake, parse_handshake,
    create_bitfield, MSG_BITFIELD,
)

HANDSHAKE_LEN = 32
MSG_LEN_PREFIX = 4

class ConnectionHandler(threading.Thread):
    
    def __init__(self, sock: socket.socket, main_peer, remote_peer_id: str = None):
        super().__init__()
        self.sock = sock
        self.main_peer = main_peer
        self.remote_peer_id = remote_peer_id
        self.daemon = True  # allows program to exit even if threads are running
        
    def run(self):
        """
        Main loop for the connection.
        1. Perform handshake.
        2. Send/Receive Bitfield.
        3. Enter the message processing loop.
        """
        try:
            # if handshake fails cleanup and exit
            if not self._perform_handshake():
                self.cleanup()
                return
            
            logger.info(f"Handshake successful with Peer {self.remote_peer_id}.")
            
            self.main_peer.neighbors[self.remote_peer_id]['socket'] = self.sock
            self.main_peer.neighbors[self.remote_peer_id]['handler_thread'] = self
            
            self._send_bitfield()
            
            # --- Main Message Loop (To be implemented) ---
            logger.info(f"Starting message loop with Peer {self.remote_peer_id}.")
            # self._message_loop() 

        except (BrokenPipeError, ConnectionResetError, EOFError) as e:
            logger.warning(f"Connection with {self.remote_peer_id or 'Unknown'} dropped: {e}")
        except Exception as e:
            logger.error(f"Error in ConnectionHandler for {self.remote_peer_id}: {e}", exc_info=True)
        finally:
            self.cleanup()

    def _perform_handshake(self) -> bool:

        # create and send handshake message
        handshake_msg = create_handshake(self.main_peer.peer_id)
        self.sock.sendall(handshake_msg)
        
        # receive handshake message
        try:
            recv_handshake = self.sock.recv(HANDSHAKE_LEN)
            if not recv_handshake or len(recv_handshake) != HANDSHAKE_LEN:
                logger.warning("Did not receive a full handshake.")
                return False
        except socket.timeout:
            logger.warning("Socket timed out waiting for handshake.")
            return False
            
        # parse the handshake
        peer_id, valid = parse_handshake(recv_handshake)
        
        if not valid:
            return False
            
        # validate peer ID
        if self.remote_peer_id:
            # we are the client, we know who we connected to.
            if peer_id != self.remote_peer_id:
                logger.warning(f"Connected to {peer_id}, but expected {self.remote_peer_id}.")
                return False
        else:
            # we are the server, we didn't know who was connecting.
            if peer_id not in self.main_peer.neighbors:
                logger.warning(f"Peer {peer_id} connected, but is not in PeerInfo.cfg.")
                return False
            self.remote_peer_id = peer_id
            # Log the "is connected from" message
            logger.info(f"Peer {self.main_peer.peer_id} is connected from Peer {self.remote_peer_id}.")

        return True

    def _send_bitfield(self):
        # func name is self-explanatory
        bitfield_payload = self.main_peer.bitfield.get_payload()
        bitfield_msg = create_bitfield(bitfield_payload)
        self.sock.sendall(bitfield_msg)
        logger.info(f"Sent bitfield to {self.remote_peer_id}.")

    def cleanup(self):
        # closes the socket and removes self from main peer state
        if self.sock:
            self.sock.close()
        
        if self.remote_peer_id and self.remote_peer_id in self.main_peer.neighbors:
            # clear state
            self.main_peer.neighbors[self.remote_peer_id]['socket'] = None
            self.main_peer.neighbors[self.remote_peer_id]['handler_thread'] = None
        
        logger.info(f"Connection with {self.remote_peer_id or 'Unknown'} cleaned up.")