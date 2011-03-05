import unittest
from pybv.vehicle import *
from numpy import deg2rad
import numpy

from geometry import assert_allclose, SE2_from_translation_angle

def equal(a, b):
    return numpy.linalg.norm(array(a).flatten() - array(b).flatten()) <= 1e-7
    
class OmniTest(unittest.TestCase):
    
    def testIntegration(self):
        """ Testing the integration of OmnidirectionalKinematics """
        
        ok = OmnidirectionalKinematics(
            max_linear_velocity=1, max_angular_velocity=1)
         
        dt = 0.1
        
        M = 1  # max
        Z = 0  # zero 
        m = -1 # min
        
        tests = [
            # format   (  (start_xy, start_theta),  commands, (final_xy, final_theta))
            (([0, 0], 0), [Z, Z, Z], ([0, 0], 0)),
            (([1, 2], 3), [Z, Z, Z], ([1, 2], 3)),
            
            (([0, 0], 0), [M, Z, Z], ([dt, 0], 0)),
            
            (([0, 0], 0), [m, Z, Z], ([-dt, 0], 0)),
            (([0, 0], 0), [Z, M, Z], ([0, dt], 0)),
            (([0, 0], 0), [Z, m, Z], ([0, -dt], 0)),
            (([0, 0], 0), [Z, Z, M], ([0, 0], dt)),
            (([0, 0], 0), [Z, Z, m], ([0, 0], -dt)),
            
            (([0, 0], deg2rad(90)), [M, Z, Z], ([0, dt], deg2rad(90))),
            (([0, 0], deg2rad(90)), [Z, M, Z], ([-dt, 0], deg2rad(90)))
            
            # TODO: add some more tests with non-zero initial rotation
        ]
        
        for initial, commands, final in tests:
            position, rotation = initial
            position_f, rotation_f = final
            
            start_state = SE2_from_translation_angle(array(position), rotation)
            expected = SE2_from_translation_angle(array(position_f), rotation_f)
            
            actual = ok.evolve_state(start_state, commands, dt)  
            
            msg = ("Transition  %s ->{%s}-> %s , received %s " % 
                (initial, commands, final, SE2.friendly(actual))) 
            
            assert_allclose(expected, actual, err_msg=msg, atol=1e-7)
            
        
