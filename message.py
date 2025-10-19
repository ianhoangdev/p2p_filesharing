import struct

MSG_CHOKE = 0
MSG_UNCHOKE = 1
MSG_INTERESTED = 2
MSG_NOT_INTERESTED = 3
MSG_HAVE = 4
MSG_BITFIELD = 5
MSG_REQUEST = 6
MSG_PIECE = 7

HANDSHAKE_HEADER = b'P2PFILESHARINGPROJ'
HANDSHAKE_ZEROBITS = b'\x00' * 10

def create_handshake(peer_id: str) -> bytes:
    # Format: [Header][Zero Bits][Peer ID]
    peer_id_bytes = struct.pack('!I', int(peer_id))
    return HANDSHAKE_HEADER + HANDSHAKE_ZEROBITS + peer_id_bytes

def parse_handshake(handshake: bytes):
    header = handshake[0:18]
    zero_bits = handshake[18:28]
    peer_id_bytes = handshake[28:32]
    
    if header != HANDSHAKE_HEADER or zero_bits != HANDSHAKE_ZEROBITS:
        return None, False
        
    # unpack the 4-byte peer ID
    peer_id = str(struct.unpack('!I', peer_id_bytes)[0])
    return peer_id, True

def create_message(msg_type: int, payload: bytes = b'') -> bytes:
    # Format: [Message Length (4 bytes)][Message Type (1 byte)][Payload]

    msg_len = 1 + len(payload)
    len_prefix = struct.pack('!I', msg_len)
    type_prefix = struct.pack('!B', msg_type)
    
    return len_prefix + type_prefix + payload

def create_have(piece_index: int) -> bytes:
    payload = struct.pack('!I', piece_index)
    return create_message(MSG_HAVE, payload)

def create_request(piece_index: int) -> bytes:
    payload = struct.pack('!I', piece_index)
    return create_message(MSG_REQUEST, payload)

def create_bitfield(bitfield_payload: bytes) -> bytes:
    return create_message(MSG_BITFIELD, bitfield_payload)

def create_piece(piece_index: int, content: bytes) -> bytes:
    index_payload = struct.pack('!I', piece_index)
    payload = index_payload + content
    return create_message(MSG_PIECE, payload)

MSG_CHOKE_BYTES = create_message(MSG_CHOKE)
MSG_UNCHOKE_BYTES = create_message(MSG_UNCHOKE)
MSG_INTERESTED_BYTES = create_message(MSG_INTERESTED)
MSG_NOT_INTERESTED_BYTES = create_message(MSG_NOT_INTERESTED)