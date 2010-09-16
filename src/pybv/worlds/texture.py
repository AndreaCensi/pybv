

class Texture:
    def __init__(self, buffer, cell_size):
        self.buffer = buffer
        self.cell_size = cell_size
        
    def __call__(self, curvilinear):
        return self.sample(curvilinear)
    
    def __eq__(self, other):
        return self.cell_size == other.cell_size and \
            self.buffer.shape == other.buffer.shape and \
            (self.buffer == other.buffer).all()
    
    def sample(self, curvilinear_coord):
        ''' buffer: represents the texture. Each cell of the buffer
            is cell_size in "real" measure. Curvilinear coordinate
            goes for 0 to len(buffer) * cell_size, then it wraps
            around the buffer '''
        index = int(curvilinear_coord / self.cell_size)
        index = index % len(self.buffer)
        return self.buffer[index]
