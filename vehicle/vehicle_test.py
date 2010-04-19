from pybv.vehicle import *
import unittest

class VehicleConstructors(unittest.TestCase):
    
    def testConstruction(self):
        """ Testing basic Vehicle constructors """
        self.assert_(Vehicle)
        
    def testDynamics(self):
        """ Trying num_commands member """
        v = Vehicle()
        self.assert_(v.config.num_commands == 0)
        v.set_dynamics(OmnidirectionalKinematics())
        self.assert_(v.config.num_commands == 3)
        v.set_dynamics(None)
        self.assert_(v.config.num_commands == 0)
        
    def testBasics(self):
        """ Testing that we define .config and its members """
        v = Vehicle()
        self.assert_(v.config is not None)
        self.assert_(v.config.sensors is not None)
   #      self.assert_(v.config.optics is not None)
   #     self.assert_(len(v.config.optics) == 0)
   #     self.assert_(v.config.rangefinder is not None)
   #     self.assert_(len(v.config.rangefinder) == 0)
        self.assert_(v.config.num_sensels == 0)
        self.assert_(v.config.num_commands == 0)
        
    def testState(self):
        """ Checking set_state() """
        v = Vehicle()
        self.assertRaises(TypeError, v.set_state, None)
        self.assertRaises(TypeError, v.set_state, 10)
        