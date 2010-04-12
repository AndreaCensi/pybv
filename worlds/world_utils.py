from pybv.utils import RigidBodyState
from numpy import random
from numpy.linalg import norm
from math import pi

def get_safe_pose(raytracer, world_radius, safe_zone, num_tries=100):
    """ Returns RigidBodyState None if num_tries tries fail """
    k = 0
    while k < num_tries: 
        k += 1
        position = random.rand(2,1) * world_radius
        if norm(position) > world_radius:
            continue
        orientation = random.rand(1) * 2 * pi
        intersect, surface = raytracer.query_circle(center=position,radius=safe_zone)
        if intersect:
            continue
        
        rbs = RigidBodyState()
        rbs.set_2d_position(position)
        rbs.set_2d_orientation(orientation)
        return rbs
        
    return None