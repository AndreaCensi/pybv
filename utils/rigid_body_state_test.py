
from pybv.utils import RigidBodyState
import unittest
from numpy import random, pi, array, ndarray
from numpy.testing import *

class CompositionTests(unittest.TestCase):
    
    def getRandom(self):
        return RigidBodyState(position=random.randn(2), attitude=random.rand(1) * pi)
        
    def testInterface(self):
        """ Testing some basic facts """
        self.assertEqual(RigidBodyState(), RigidBodyState())
        self.assertRaises(TypeError, RigidBodyState().__eq__, None)
        self.assertRaises(TypeError, RigidBodyState().__eq__, 42)
        self.assertRaises(TypeError, RigidBodyState().oplus, None)
        self.assertRaises(TypeError, RigidBodyState().oplus, 42)
  
    def testInitialization(self):
        """ identity is properly initialized """
        identity = RigidBodyState()
        assert_almost_equal(identity.position, array([[0], [0], [0]]))
        assert_almost_equal(identity.attitude, array([[1, 0, 0], [0, 1, 0], [0, 0, 1]]))
        
        self.assertRaises((TypeError, ValueError), RigidBodyState, position=1)
        self.assertRaises((TypeError, ValueError), RigidBodyState, position=[1, 2, 3, 4])
        self.assertRaises((TypeError, ValueError), RigidBodyState, attitude=[1, 2, 3, 4])

        self.assertTrue(isinstance(RigidBodyState(position=[0, 0]).position, ndarray))
        self.assertEqual(RigidBodyState(position=[0, 0]).position.shape, (3, 1))
        self.assertEqual(RigidBodyState(attitude=0).attitude.shape, (3, 3))

    def testInit2(self):
        """ attitude can be initialized with 1d array """
        RigidBodyState([0, 0], array([0]))
        
  
    def testIdentity(self):
        """ Test that identity is neutral element """
        a = self.getRandom()
        b = self.getRandom()
        c = self.getRandom()
        identity = RigidBodyState()
        D = a.oplus(b)
        self.assertSamePose(identity, identity)
        self.assertSamePose(identity, a.inverse().oplus(a))
        self.assertSamePose(identity, a.oplus(a.inverse()))
        self.assertSamePose(b, a.inverse().oplus(D))
        self.assertSamePose(a, D.oplus(b.inverse()))
         
    def assertSamePose(self, a, b):
        msg = " %s == %s (distance = %s ) " % (a, b, a.distance(b))
        self.assertTrue(a.__eq__(b), msg)    
    
        
