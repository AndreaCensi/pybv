
from pybv.utils import RigidBodyState
import unittest
from numpy import random, pi, array
from numpy.testing import *

class CompositionTests(unittest.TestCase):
    
    def getRandom(self):
        rbs = RigidBodyState()
        rbs.set_2d_position( random.randn(2) )
        rbs.set_2d_orientation( random.rand(1) * pi )
        return rbs
        
    def testInterface(self):
        """ Testing some basic facts """
        self.assertEqual( RigidBodyState(), RigidBodyState() )
        self.assertRaises( TypeError, RigidBodyState().__eq__, None )
        self.assertRaises( TypeError, RigidBodyState().__eq__, 42 )
        self.assertRaises( TypeError, RigidBodyState().oplus, None )
        self.assertRaises( TypeError, RigidBodyState().oplus, 42 )
  
    def testInitialization(self):
        """ identity is properly initialized """
        identity = RigidBodyState()
        assert_almost_equal( identity.position, array([[0],[0],[0]]) )
        assert_almost_equal( identity.attitude, array([[1,0,0],[0,1,0],[0,0,1]]) )
  
    def testIdentity(self):
        """ Test that identity is neutral element """
        a = self.getRandom()
        b = self.getRandom()
        c = self.getRandom()
        identity = RigidBodyState()
        D = a.oplus(b)
        self.assertSamePose(identity, identity )
        self.assertSamePose(identity, a.inverse().oplus(a) )
        self.assertSamePose(identity, a.oplus(a.inverse()) )
        self.assertSamePose(b, a.inverse().oplus(D))
        self.assertSamePose(a, D.oplus(b.inverse()))
         
    def assertSamePose(self, a, b):
        msg = " %s == %s (distance = %s ) " % (a,b, a.distance(b) )
        self.assertTrue( a.__eq__(b), msg)    
    
        