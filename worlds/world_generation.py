import numpy
from numpy import *

def create_random_world(radius):
    objects = []
    
    # create arena
    texture = 'lambda x: cos(x)'
    
    objects.append( 
        { "class": "circle", "surface": 0, "radius": radius, "center": [0.0,0.0], "texture": texture, "solid_inside": 0}
    )
    
    
    num_lines = 10
    length = radius / 30.0
    
    for x in range(num_lines):
        p1 = radius * 2 * (numpy.random.rand(2)-0.5);
        diff = 3 * length * numpy.random.randn(2)
        p2 = p1 + diff
        col = 0.3 + numpy.random.rand(1) * 0.5
        texture = "lambda x: %f" % col
        objects.append( { "class": "polyline", "surface": x+10, "points": [list(p1), list(p2)], "texture": texture})


    olfaction_sources = []    
    num_sources = 10
    for x in range(num_sources):
        position = list(radius * 2 * (numpy.random.rand(2)-0.5))
        position.append(1)
        scale = numpy.random.rand(1) * radius
        dist_func = "lambda dist: math.exp(- dist / %f ) " % scale
        olfaction_sources.append( {  "position": position, 'components': { 'food': dist_func } })
        
    world = {"class": "map", "objects": objects, "olfaction_sources": olfaction_sources}
    
    return world 
