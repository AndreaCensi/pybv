import unittest

from pybv.sensors import OlfactionSensor
from pybv.utils import RigidBodyState
import math, numpy


class ParsingTest(unittest.TestCase):
    
    map_valid = [{ 
           'olfaction_sources': [
                       {'position': [0,0,0],  'components': 
                            { 'food': lambda dist: math.exp(-dist/3) }  
                        }
            ]
    },{ 
           'olfaction_sources': [
                       {'position': [0,0,0],  'components': 
                            { 'food': 3 }  
                        }
            ]
    }]
    map_invalid = [None,42,{}, 
                { 'olfaction_sources': None },
                { 'olfaction_sources': 42 },
                { 'olfaction_sources': [42] },
                { 'olfaction_sources': [None] },
                { 'olfaction_sources': [{}] },
                { 'olfaction_sources': [{'position': None}] },
                { 'olfaction_sources': [{'position': 42}] },
                { 'olfaction_sources': [{'position': [0,0], 'components': None }] },
                { 'olfaction_sources': [{'position': [0,0], 'components': [] }] },
                { 'olfaction_sources': [{'position': [0,0], 'components': {132: 0} }] },
                { 'olfaction_sources': [{'position': [0,0], 'components': {} }] },
                { 'olfaction_sources': [{'position': [0,0], 'components': {'food': 'bah' } }] }
    ]
    
    def testParsing(self):
        """ Trying to parse a simple map """
        for map in ParsingTest.map_valid:
            os = OlfactionSensor()
            os.set_map(map)
            os.add_receptor(pose = RigidBodyState(), sensitivity = {'food': 1})
            os.compute_observations(RigidBodyState(position = [10,0,0]) )
            self.assertTrue(True)
    
        
        
    def testParsingInvalid(self):
        for map in ParsingTest.map_invalid:
            os = OlfactionSensor()
            msg = map.__str__()
            print msg
            self.assertRaises( (TypeError, ValueError), os.set_map, map )
        
        