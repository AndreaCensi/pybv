import unittest
from numpy import *
import numpy

from pybv import BVException
from pybv.sensors import ImageRangeSensor, Rangefinder, Optics
from pybv.utils import RigidBodyState
from pybv.worlds import create_random_world


example_world = { 
	"class": "map", 
	"objects": [
		{ 
			"class": "polyline", "surface": 0,  
			"points": [ [-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1] ],
			"texture":  "lambda x: sign(sin(x))"
		},
		{
		 	"class": "circle", "surface": 1,  "radius": 10, "center": [0,0], 
			"solid_inside": 0, "texture": "lambda x: 0"
		}
	]
}

class ExampleNotset(unittest.TestCase):

    def testInitWorld(self):
        """ Make sure that there is an expection if world not passed """
        raytracer = Rangefinder()
        raytracer.add_photoreceptors([0],0.01,0.01)
        self.assertRaises( BVException, raytracer.render, RigidBodyState() )
        
    def testInitSensor(self):
        """ Make sure that there is an expection if photoreceptors not defined """
        raytracer = Rangefinder()
        raytracer.set_map(example_world)
        self.assertRaises( BVException, raytracer.render, RigidBodyState() )
        
        
class SensorPickling(unittest.TestCase):
	def testPickling(self):
        raytracer = Rangefinder(min_num_aux=1)
        raytracer.set_map(world)
        raytracer.add_photoreceptors( linspace(-deg2rad(170), deg2rad(170), 180),
									spatial_sigma=deg2rad(0.5), sigma = 0.01 )

        raytracer2 = make_sure_pickable( raytracer )
        raytracer2.render(RigidBodyState())

    
class ExampleCircle(unittest.TestCase):
    def try_with(self, center, radius, position, orientation):
        world = { 
        	"class": "map", 
        	"objects": [
        		{
        		 	"class": "circle", "surface": 1,  "radius": radius, "center": center, "texture": "lambda x: 0",
        			"solid_inside": 0
        		}
        	]
        }
        
        raytracer = Rangefinder(min_num_aux=1)
        raytracer.set_map(world)
        raytracer.add_photoreceptors( linspace(-deg2rad(170), deg2rad(170), 180), 
            spatial_sigma=deg2rad(0.5), sigma = 0.01 )
        
        rbs = RigidBodyState()
        rbs.set_2d_position(position)
        rbs.set_2d_orientation(orientation)
        
        data = raytracer.render(rbs)

        # given min_num_aux and spatial_sigma < 1, we expect
        # only one aux ray per photoreceptors
        for indices in raytracer.aux_indices:
            self.assertEqual( len(indices), 1)
            
        # The direction should remain the same
        for i in range(len(raytracer.directions)):
            j = raytracer.aux_indices[i][0]
            self.assertEqual( i,  j)
            self.assertEqual( rad2deg(raytracer.directions[i]),
                rad2deg(raytracer.aux_directions[j] ))
                
        # If we are inside the circle, then everything should be valid
        if linalg.norm( array(position) - array(center) ) < radius:
            for valid in data['valid']:
                self.assertEqual(valid, 1)
            
        phi_world = numpy.array(raytracer.directions) + orientation
        rho  = numpy.array(data['readings'])
        points = vstack( [ cos(phi_world) * rho, sin(phi_world) * rho ] )
        
        center_world = array(center) - array(position)

        for i in range(points.shape[1]):
            if not data['valid'][i]:
                continue
            distance_to_center = linalg.norm( points[:, i] - center_world )
            self.assertAlmostEqual(distance_to_center, radius, 5)
        
    def testCircleRaytracing(self):
        """ Testing circle raytracing """
        self.try_with(center=[10,10], radius=10, position=[15,10], orientation=20)
        self.try_with(center=[10,10], radius=10, position=[25,10], orientation=0)

    def testLineRaytracing(self):
    	""" Testing segments raytracing """
        # TODO: write this test
        pass
       
    def setUp(self):
        self.raytracer = Rangefinder()
        self.example_world = { 
        	"class": "map", 
        	"objects": [
        		{ 
        			"class": "polyline", "surface": 0,  
        			"points": [ [-1, -1], [-1, 1], [1, 1], [1, -1], [-1, -1] ],
        			"texture":  "lambda x: sign(sin(x))"
        		},
        		{
        		 	"class": "circle", "surface": 1,  "radius": 10, "center": [0,0],  "texture": "lambda x: 0",
        			"solid_inside": 0
        		}
        	]
        }
        self.raytracer.set_map(self.example_world)
        
        
class WorldGeneration2(unittest.TestCase):
	def testWorldGeneration(self):
		""" Testing if we can parse the output of world generation utils """
		sensor = Rangefinder()
		sensor.set_map(create_random_world(10))
