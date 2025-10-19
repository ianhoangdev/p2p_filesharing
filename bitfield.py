import math
class Bitfield:
    def __init__(self, file_size, piece_size, has_file=False):
        self.piece_size = piece_size
        self.piece_size = piece_size

        self.total_pieces = math.ceil(file_size / piece_size)
        num_bytes = math.ceil(self.total_pieces / 8)

        # use bytearray instead of normal array 
        # -> 1 bit per piece instead of 1 byte per piece
        self.bitfield = bytearray(num_bytes)

        # if has_file is True, set all pieces to 1
        if has_file: self.set_all_pieces()
    
    def set_all_pieces(self):
        for i in range(len(self.bitfield)):
            self.bitfield[i] = 0xFF
    
    def has_piece(self, piece_index):
        byte_index = piece_index // 8
        bit_index = piece_index % 8

