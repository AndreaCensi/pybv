from pybv.worlds import create_random_world
from pybv.sensors import ImageRangeSensor
from pybv.utils import RigidBodyState

from numpy import deg2rad, linspace, pi
from time import time

world = create_random_world(radius=10)

sensor = ImageRangeSensor(world=world)
sensor.add_photoreceptors(linspace(-pi/2, pi/2, 100), spatial_sigma=deg2rad(5), sigma=0.01)
sensor.add_photoreceptors(linspace(-pi/6, pi/6,  20), spatial_sigma=deg2rad(2), sigma=0.01)


t0 = time(); ntrials=100
for i in range(ntrials):
    rbs = RigidBodyState()
    answer = sensor.render(rbs)
    
T = time() - t0


print answer

print "Average time:", T / ntrials




