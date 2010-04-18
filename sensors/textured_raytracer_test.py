import unittest
from copy import deepcopy
from pybv import BVException
from pybv.sensors import TexturedRaytracer
from pybv.utils import make_sure_pickable
from pybv.worlds import create_random_world

class Setup(unittest.TestCase):
    
    def testInstantiation(self):
        """ Check we can connect to default executable """
        self.assert_( TexturedRaytracer )
        
    def testWrongcommand(self):
        """ Check an exception is raised if wrong raytracer exec is passed """
        self.assertRaises( BVException, TexturedRaytracer, 'raytracer_not')
        
        
class WorldInterpretation(unittest.TestCase):
            
    def setUp(self):
        self.raytracer = TexturedRaytracer()
        self.example_world = { 
        	"class": "map", 
        	"objects": [
        		{ 
        			"class": "polyline", "surface": 0,  
        			"points": [ [-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1] ],
        			"texture":  "lambda x: sign(sin(x))"
        		},
        		{
        		 	"class": "circle", "surface": 1,  "radius": 10, "center": [0,0],  "texture": 0,
        			"solid_inside": 0
        		}
        	]
        }
    
    def testWorldInterpretation(self):
        """ Trying to load a canonical example map """
        self.assert_(self.raytracer.set_map, self.example_world)

    def testArgChecking(self):
        """ Trying some invalid inputs """
        self.assertRaises(TypeError, self.raytracer.set_map, None)
        self.assertRaises(BVException, self.raytracer.set_map, {})
        # TODO: write more tests for map format
 
    def testPickling(self):
        """ Make sure we can pickle this sensor """
        make_sure_pickable( self.raytracer )
    
    def testPickling(self):
        """ Pickling after map loading """
        self.raytracer.set_map(create_random_world(10))
        make_sure_pickable(self.raytracer)
        
    def testIntegrity(self):
        """ Make sure that this sensor does not modify the map object """
        map =  create_random_world(10)
        map_original = deepcopy(map)
        self.raytracer.set_map(map)
        self.assertEqual(map, map_original)

        