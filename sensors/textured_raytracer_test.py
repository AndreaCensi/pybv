import unittest
from pybv import BVException
from pybv.sensors import TexturedRaytracer

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
