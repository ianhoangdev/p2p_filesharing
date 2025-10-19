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
    