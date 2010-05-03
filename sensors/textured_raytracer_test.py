import unittest
from copy import deepcopy
from numpy import isnan, array
from pybv import BVException
from pybv.sensors import TexturedRaytracer
from pybv.utils import make_sure_pickable
from pybv.worlds import create_random_world

class Setup(unittest.TestCase):
    
    def testInstantiation(self):
        """ Check we can connect to default executable """
        self.assert_(TexturedRaytracer)
        
        
class WorldInterpretation(unittest.TestCase):
            
    def setUp(self):
        self.raytracer = TexturedRaytracer()
        self.example_world = { 
        	"class": "map",
        	"objects": [
        		{ 
        			"class": "polyline", "surface": 0,
        			"points": [ [-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1] ],
        			"texture":  "lambda x: numpy.sign(numpy.sin(x))"
        		},
        		{
        		 	"class": "circle", "surface": 1, "radius": 10, "center": [0, 0],
                     "texture": 0,
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
        make_sure_pickable(self.raytracer)

    def testPickling3(self):
        """ Make sure we can pickle this sensor twice """
        r2 = make_sure_pickable(self.raytracer)
        make_sure_pickable(r2)
    
    def testPickling2(self):
        """ Pickling after map loading """
        self.raytracer.set_map(create_random_world(10))
        make_sure_pickable(self.raytracer)
            
    def testWrongcommand(self):
        """ Check an exception is raised if wrong raytracer exec is passed """
        raytracer = TexturedRaytracer('raytracer_not')
        raytracer.set_map(self.example_world)
        self.assertRaises(BVException,
                          raytracer.query_circle, center=[0, 0], radius=1)

    def testIntegrity(self):
        """ Make sure that this sensor does not modify the map object """
        map = create_random_world(10)
        map_original = deepcopy(map)
        self.raytracer.set_map(map)
        self.assertEqual(map, map_original)

example_sensor = { 
    "class": "sensor",
    "directions": [-1.57, -0.78, 0, 0.78, 1.57]
}

empty_world = { "class": "map",
            "objects": [] }
example_world = {
            "class": "map",
            "objects": [
                { 
                    "class": "polyline", "surface": 0,
                    "points": [ [-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1] ],
                    "texture":  "lambda x: numpy.sign(numpy.sin(x))"
                },
                {
                     "class": "circle", "surface": 1, "radius": 10, "center": [0, 0],
                     "texture": 0,
                    "solid_inside": 0
                }
            ]
        }

class SensorSpec(unittest.TestCase):
    
    def testSensorSpec0(self):
        """ Making sure that an exception is thrown if sensor is not specified """
        raytracer = TexturedRaytracer()
        raytracer.set_map(example_world)
        self.assertRaises(BVException, raytracer.query_sensor, [0, 0], 0)
    
    def testSensorSpec1(self):
        """ Making sure that the sensor spec survives the pickling """
        raytracer = TexturedRaytracer()
        raytracer.set_map(example_world)
        raytracer.set_sensor(example_sensor)
        data1 = raytracer.query_sensor([0, 0], 0)
        raytracer2 = make_sure_pickable(raytracer)
        data2 = raytracer2.query_sensor([0, 0], 0)
        self.assertEqual(data1['readings'], data2['readings'])

    def testMapIsReset(self):
        """ Making sure that the map is overwritten """
        raytracer = TexturedRaytracer()
        raytracer.set_sensor(example_sensor)
        
        raytracer.set_map(empty_world)
        data1 = raytracer.query_sensor([0, 0], 0)
        readings = array(data1['readings'], dtype='float32')
        self.assertTrue(isnan(readings).all())

        raytracer.set_map(example_world)
        data1 = raytracer.query_sensor([0, 0], 0)
        readings = array(data1['readings'], dtype='float32')
        self.assertTrue(not isnan(readings).any())

        raytracer.set_map(empty_world)
        data1 = raytracer.query_sensor([0, 0], 0)
        readings = array(data1['readings'], dtype='float32')
        self.assertTrue(isnan(readings).all())


    def testQueryCircle(self):
        ''' Raises if map not specified '''
        raytracer = TexturedRaytracer()
        self.assertRaises(BVException,
                          raytracer.query_circle, center=[0, 0], radius=1)    
    
class QueryCircleWithSegment(unittest.TestCase):
    def setUp(self):
        example_world = { 
            "class": "map",
            "objects": [
                { 
                    "class": "polyline", "surface": 0,
                    "points": [ [0, 0], [1, 0]],
                    "texture":  "lambda x: sign(sin(x))"
                }
            ]
        }
        self.raytracer = TexturedRaytracer()
        self.raytracer.set_map(example_world)
    
    # todo, raises if radius < 0
    def testRaise(self):
        ''' check raises if invalid parameters '''
        r = self.raytracer
        self.assertRaises(ValueError, r.query_circle, [0, 0], -1)
        self.assertRaises(ValueError, r.query_circle, [0, 0], 0)
        self.assertRaises(ValueError, r.query_circle, [0, 0], float('nan'))
        self.assertRaises(ValueError, r.query_circle, [None, 0], 1)
        self.assertRaises(ValueError, r.query_circle, [float('nan'), 0], 1)
        self.assertRaises(ValueError, r.query_circle, None, 1)
        self.assertRaises(ValueError, r.query_circle, 'ciao', 1)
        
    def testIntersection(self):
        ''' Simple intersections tests '''
        surf = 0
        r = self.raytracer
        eps = 0.0001
        self.assertEqual((True, surf), r.query_circle([0, 0], 1))
        self.assertEqual((True, surf), r.query_circle([-1, 0], 1 + eps))
        self.assertEqual((False, None), r.query_circle([-1, 0], 1 - eps))
        self.assertEqual((True, surf), r.query_circle([2, 0], 1 + eps))
        self.assertEqual((False, None), r.query_circle([2, 0], 1 - eps))
        self.assertEqual((True, surf), r.query_circle([0.5, 0.5], 0.5 + eps))
        self.assertEqual((False, None), r.query_circle([0.5, 0.5], 0.5 - eps))
    

eps = 0.0001 
        
class QueryCircleWithHollowCircle(unittest.TestCase):
    def setup(self, solid_inside):
        example_world = { 
            "class": "map",
            "objects": [
                {  
                    "class": "circle", "surface": 0, "radius": 1,
                    "center": [0, 0],
                    "solid_inside": solid_inside,
                    "texture":  "lambda x: sign(sin(x))"
                }
            ]
        }
        raytracer = TexturedRaytracer()
        raytracer.set_map(example_world)
        return raytracer
        
    def testIntersection1(self):
        ''' Checking from inside, hollow '''
        r = self.setup(solid_inside=0)
        self.assertEqual((True, 0), r.query_circle([0, 0], 1 + eps))
        self.assertEqual((False, None), r.query_circle([0, 0], 1 - eps))
    
    def testIntersection2(self):
        ''' Checking from inside, solid '''
        r = self.setup(solid_inside=1)
        self.assertEqual((True, 0), r.query_circle([0, 0], 1 + eps))
        self.assertEqual((True, 0), r.query_circle([0, 0], 1 - eps))
        
    def testIntersection3(self):
        ''' Checking from outside, hollow '''
        r = self. setup(solid_inside=0)
        self.assertEqual((True, 0), r.query_circle([-2, 0], 1 + eps))
        self.assertEqual((False, None), r.query_circle([-2, 0], 1 - eps))

    def testIntersection4(self):
        ''' Checking from outside, solid '''
        r = self.setup(solid_inside=1)
        self.assertEqual((True, 0), r.query_circle([-2, 0], 1 + eps))
        self.assertEqual((False, None), r.query_circle([-2, 0], 1 - eps))
        
