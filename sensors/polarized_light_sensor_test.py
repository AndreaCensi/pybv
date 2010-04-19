import unittest
from numpy import array
from pybv.sensors import PolarizedLightSensor
from pybv.utils import RigidBodyState, assert_1d_ndarray

class TestBasics(unittest.TestCase):
    
    def testInitialization(self):
        """ PolarizedLightSensor initialization of parameters """
        self.assertRaises(Exception, PolarizedLightSensor)
        self.assertRaises(Exception, PolarizedLightSensor, None)
        self.assertRaises(ValueError, PolarizedLightSensor, -2)
        self.assertRaises(ValueError, PolarizedLightSensor, 0)
        
    def testUse(self):
        pls = PolarizedLightSensor(45)
        self.assertEqual(len(pls.directions), 45)
        pose1 = RigidBodyState(attitude=0.1)
        data1 = pls.compute_observations(pose1)
        
        self.assertTrue( 'response' in data1)
        self.assertTrue( 'sensels' in data1)
        self.assertTrue( assert_1d_ndarray(array(data1['sensels'])) )
        self.assertTrue( assert_1d_ndarray(array(data1['response'])) )
        