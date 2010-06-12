from numpy import isnan, isinf
from pybv import BVException

class gt:
    def __init__(self, n):
        self.n = n
    def __eq__(self, other):
        return other > self.n
    
    def __str__(self):
        return '>%s' % self.n 

class square_shape:
    def __eq__(self, other):
        return len(other) == 2  and other[0] == other[1] 

def require_shape(expected_shape, v):
    if not expected_shape == v.shape:
        raise ValueError('Expecting shape %s, got %s' % 
                         (expected_shape, v.shape))  

def assert_reasonable_value(a):
    reasonable = not isnan(a).any() and not isinf(a).any()
    if not reasonable:
        raise BVException('Invalid value %s' % a)
