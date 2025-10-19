import math
class Bitfield:
    def __init__(self, file_size, piece_size, has_file=0):
        self.piece_size = piece_size
        self.piece_size = piece_size

        self.total_pieces = math.ceil(file_size / piece_size)
        num_bytes = math.ceil(self.total_pieces / 8)

        # use bytearray instead of normal array 
        # -> 1 bit per piece instead of 1 byte per piece
        self.bitfield = bytearray(num_bytes)

        # if has_file is 1 / True, set all pieces to 1
        if has_file == 1: self.set_all_pieces()
    
    def set_all_pieces(self):
        for i in range(len(self.bitfield)):
            self.bitfield[i] = 0xFF
    
    def has_piece(self, piece_index):
        byte_index = piece_index // 8
        bit_index = piece_index % 8

        # creates a binary number with only one bit turned on
        mask = 1 << (7 - bit_index)

        return (self.bitfield[byte_index] & mask) != 0
    
    def set_piece(self, piece_index):
        byte_index = piece_index // 8
        bit_index = piece_index % 8
        
        # turn on only the bit at bit_index
        mask = 1 << (7 - bit_index)

        # |= is the bitwise OR assignment op
        self.bitfield[byte_index] |= mask

    def compare(self, other_bitfield):
        # basically get bits that other has but self doesn't
        interesting_pieces = []
        for i in range(self.total_pieces):
            if other_bitfield.has_piece(i) and not self.has_piece(i):
                interesting_pieces.append(i)
        return interesting_pieces
    
    def is_complete(self):
        for i in range(self.total_pieces):
            if not self.has_piece(i):
                return False
        return True
    
    def update_from_payload(self, payload: bytes):
        self.bitfield = bytearray(payload)
    
    def get_payload(self) -> bytes:
        return bytes(self.bitfield)