import unittest

from pybv.sensors import OlfactionSensor
from pybv.utils import RigidBodyState
from pybv.worlds import create_random_world
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
    },{ 
           'olfaction_sources': [
                       {'position': [0,0,0],  'components': 
                            { 'food': "lambda x: x * 2" }  
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
            os = self.createSimpleOlfactionSensor()
            os.set_map(map)
            os.add_receptor(pose = RigidBodyState(), sensitivity = {'food': 1})
            os.compute_observations(RigidBodyState(position = [10,0,0]) )
            self.assertTrue(True)
        
    def testParsingInvalid(self):
        """ Recognizing format errors """
        for map in ParsingTest.map_invalid:
            os = self.createSimpleOlfactionSensor()
            msg = map.__str__()
            self.assertRaises( (TypeError, ValueError), os.set_map, map )
        
    def testRandomGeneration(self):
        """ Test if we can interpret a map from create_random_world() """
        world = create_random_world(10)
        os = self.createSimpleOlfactionSensor()
        os.set_map(world)
        os.compute_observations(RigidBodyState())
        
        
    def createSimpleOlfactionSensor(self):
        os = OlfactionSensor()
        os.add_receptor(RigidBodyState(position=[0.3,0]), { 'food': 1 } )
        return os
        
        
        
        