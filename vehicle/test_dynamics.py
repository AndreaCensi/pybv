import unittest
from pybv.vehicle import *
from numpy import array, deg2rad
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
        
        M = 1  # max
        Z = 0  # zero 
        m = -1 # min
        
        tests = [
            # format   (  (start_xy, start_theta),  commands, (final_xy, final_theta))
            (  ([0,0],0),  [Z,Z,Z],  ([0,0],0)),
            (  ([1,2],3),  [Z,Z,Z],  ([1,2],3)),
            
            (  ([0,0],0),  [M,Z,Z],  ([dt,0],0)),
            
            (  ([0,0],0),  [m,Z,Z],  ([-dt,0],0)),
            (  ([0,0],0),  [Z,M,Z],  ([0,dt],0)),
            (  ([0,0],0),  [Z,m,Z],  ([0,-dt],0)),
            (  ([0,0],0),  [Z,Z,M],  ([0,0], dt)),
            (  ([0,0],0),  [Z,Z,m],  ([0,0], -dt)),
            
            (  ([0,0],deg2rad(90)),  [M,Z,Z],  ([0,dt],deg2rad(90))),
            (  ([0,0],deg2rad(90)),  [Z,M,Z],  ([-dt,0],deg2rad(90)))
            
            # TODO: add some more tests with non-zero initial rotation
        ]
        
        for initial, commands, final in tests:
            
            start_state = RigidBodyState()
            start_state.set_2d_position( initial[0])
            start_state.set_2d_orientation( initial[1])

            actual = ok.evolve_state(start_state, commands, dt)  
            
            msg = "Transition  %s ->{%s}-> %s , received %s %s " % (initial, commands, final, actual.get_2d_position().flatten(),     actual.get_2d_orientation())
            self.assertTrue( equal(actual.get_2d_position(), final[0]), msg )
            self.assertTrue( equal(actual.get_2d_orientation(), final[1]), msg )
            
        