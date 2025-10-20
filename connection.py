import socket
import threading
import struct
from logger import logger
from message import (
    create_handshake, parse_handshake,
    create_bitfield, create_have, create_request, create_piece,
    MSG_CHOKE, MSG_UNCHOKE, MSG_INTERESTED, MSG_NOT_INTERESTED,
    MSG_HAVE, MSG_BITFIELD, MSG_REQUEST, MSG_PIECE,
    MSG_INTERESTED_BYTES, MSG_NOT_INTERESTED_BYTE
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

            while True:
                # step 1: read msg length (4 bytes), this is a blocking call
                len_prefix_bytes = self.sock.recv(MSG_LEN_PREFIX)
                
                if not len_prefix_bytes:
                    logger.info(f"Connection closed by {self.remote_peer_id} (no len_prefix).")
                    break
                
                if len(len_prefix_bytes) < MSG_LEN_PREFIX:
                    logger.warning(f"Received incomplete len_prefix from {self.remote_peer_id}.")
                    break
                
                # step 2: unpack length
                # msg_len = length of (msg type + payload)
                msg_len = struct.unpack('!I', len_prefix_bytes)[0]
                
                if msg_len == 0:
                    logger.debug(f"Received keep-alive from {self.remote_peer_id}.")
                    continue
                
                # step 3: read msg body (msg type + payload)
                msg_body = self.sock.recv(msg_len)
                
                if not msg_body:
                    logger.warning(f"Connection closed by {self.remote_peer_id} (no msg_body).")
                    break
                
                if len(msg_body) < msg_len:
                    logger.warning(f"Received incomplete message body from {self.remote_peer_id}.")
                    break
                
                # step 4: parse body
                msg_type = msg_body[0]
                payload = msg_body[1:]
                
                # step 5: handle message (to be implemented)
                self._handle_message(msg_type, payload)

        except (BrokenPipeError, ConnectionResetError, EOFError) as e:
            logger.warning(f"Connection with {self.remote_peer_id or 'Unknown'} dropped: {e}")
        except Exception as e:
            logger.error(f"Error in ConnectionHandler for {self.remote_peer_id}: {e}", exc_info=True)
        finally:
            self.cleanup()
    
    def _handle_message(self, msg_type: int, payload: bytes):
        # handling all incoming messages
        logger.debug(f"Received message type {msg_type} from {self.remote_peer_id} with payload len {len(payload)}")
        if msg_type == MSG_CHOKE:
            ...
        elif msg_type == MSG_UNCHOKE:
            ...
        elif msg_type == MSG_INTERESTED:
            ...
        elif msg_type == MSG_NOT_INTERESTED:
            ...
        elif msg_type == MSG_HAVE:
            ...
        elif msg_type == MSG_BITFIELD:
            ...
        elif msg_type == MSG_REQUEST:
            ...
        elif msg_type == MSG_PIECE:
            ...

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