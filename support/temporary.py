from numpy import *

def create_random_world(radius):
    objects = []
    
    # create arena
    texture = lambda x: sin(x)
    
    objects.append( 
        { "class": "circle", "surface": 0, "radius": radius, "center": [0.0,0.0], "texture": texture}
    )
    
    
    world = {"class": "map", "objects": objects}
    
    return world 
    