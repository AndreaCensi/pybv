# 
# optics = 'ring_fog180_num180'
# world = 'cylinder'
# 
# fsee = FSeeSimulation(world=world, optics=optics)
# fsee.fsee_sensor = 
from temporary import *
from image_range_sensor import *
from textured_raytracer import *
from numpy import deg2rad

world = create_random_world(radius=10)

#print world

sensor = ImageRangeSensor()
sensor.add_photoreceptors(linspace(-pi/2, pi/2, 100), spatial_sigma=deg2rad(5), sigma=0.01)
sensor.add_photoreceptors(linspace(-pi/6, pi/6, 20), spatial_sigma=deg2rad(2), sigma=0.01)
sensor_def = sensor.get_raw_sensor()

#print sensor_def

tr = TexturedRaytracer()
tr.set_map(world)
tr.set_sensor(sensor_def)


answer = tr.query({"class":"query","position": [-15,0], "orientation": 0})
print answer 

answer = sensor.process_raw_data(answer)

print answer