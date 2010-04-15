import unittest
from pybv.vehicle import *
from numpy import array
import numpy

def equal(a,b):
    return numpy.linalg.norm( array(a).flatten() - array(b).flatten()) <= 1e-7
    
class OmniTest(unittest.TestCase):
    
    def testIntegration(self):
        """ Testing the integration of OmnidirectionalKinematics """
        
        ok = OmnidirectionalKinematics(
            max_linear_velocity=1, max_angular_velocity=1)
        
        zero = RigidBodyState()
        dt = 0.1
        
        tests = [
            # format   (  (start_xy, start_theta),  commands, (final_xy, final_theta))
            (  ([0,0],0),  [0.5,0.5,0.5],  ([0,0],0)),
            (  ([1,2],3),  [0.5,0.5,0.5],  ([1,2],3)),
            
            (  ([0,0],0),  [1,0.5,0.5],  ([dt,0],0)),
            
            (  ([0,0],0),  [0,0.5,0.5],  ([-dt,0],0)),
            (  ([0,0],0),  [0.5,1,0.5],  ([0,dt],0)),
            (  ([0,0],0),  [0.5,0,0.5],  ([0,-dt],0)),
            (  ([0,0],0),  [0.5,0.5,1],  ([0,0], dt)),
            (  ([0,0],0),  [0.5,0.5,0],  ([0,0], -dt))
            # TODO: add some more tests with non-zero initial rotation
        ]
        
        for initial, commands, final in tests:
            
            start_state = RigidBodyState()
            start_state.set_2d_position( initial[0])
            start_state.set_2d_orientation( initial[1])

            actual = ok.evolve_state(start_state, commands, dt)  
            
            self.assert_( equal(actual.get_2d_position(), final[0]) )
            self.assert_( equal(actual.get_2d_orientation(), final[1]) )
            
        