from unittest import TestCase
from numpy import array, random, zeros
from pybv.worlds.texture_generation import loop_convolve
from numpy.ma.testutils import assert_almost_equal

class loop_convolve_test(TestCase):
    
    def test_identity(self):
        n = 10
        x = random.rand(n)
        filter = array([1])
        xf = loop_convolve(x, filter)
        assert_almost_equal(x, xf)
    
    def test_raises(self):
        ''' We need unidimensional vectors '''
        self.assertRaises(ValueError, loop_convolve, zeros((2, 2)), array([1]))
        self.assertRaises(ValueError, loop_convolve, array([1]), zeros((2, 2)))
