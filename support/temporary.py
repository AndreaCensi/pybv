import numpy
from numpy import *

def create_random_world(radius):
    objects = []
    
    # create arena
    texture = lambda x: sin(x)
    
    objects.append( 
        { "class": "circle", "surface": 0, "radius": radius, "center": [0.0,0.0], "texture": texture}
    )
    
    
    world = {"class": "map", "objects": objects}
    
    
    num_lines = 10
    length = radius / 30.0
    
    for x in range(num_lines):
        p1 = radius * 2 * (numpy.random.rand(2)-0.5);
        diff = 3 * length * numpy.random.randn(2)
        p2 = p1 + diff
        col = 0.3 + numpy.random.rand(1) * 0.5
        texture = lambda x: col
        objects.append( { "class": "polyline", "surface": x+10, "points": [list(p1), list(p2)], "texture": texture})

    
    return world 
    