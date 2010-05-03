import cairo
from pybv.worlds.world_generation import create_random_world
from pybv.worlds.world_utils import get_safe_pose
from pybv.drawing.world_plot_cairo import draw_world, draw_vehicle, draw_rangefinder, \
draw_optics
from pybv.vehicle import Vehicle
from pybv.sensors import Optics
from numpy import pi, linspace, deg2rad, rad2deg, sin, cos
from pybv.sensors.textured_raytracer import TexturedRaytracer
from pybv.sensors.image_range_sensor import Rangefinder
import sys

safe_zone = 1

def simple_drawing(world, vehicle, pose, data):
    width, height = 6000, 6000
    # surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, width, height)
    surface = cairo.PDFSurface("world.pdf", width, height)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb (0, 0.3, 0.1)
    ctx.set_operator (cairo.OPERATOR_SOURCE)
    ctx.paint()
    
    box = 10
    ctx.save()
    ctx.translate(width / 2, height / 2)
    ctx.scale(0.5 * width / box, 0.5 * height / box)
    ctx.scale(1, -1)
    ctx.rectangle(-box, -box, 2 * box, 2 * box)
    #ctx.set_source_rgb(0, 1, 0)
    #ctx.stroke()
    ctx.clip() 
    
    draw_world(ctx, world)
    
    p = pose.get_2d_position()
    
    ctx.save()
    ctx.arc(p[0], p[1], safe_zone, 0, 2 * pi)
    ctx.set_source_rgba(1, 0, 0, 0.5)
    ctx.fill()
    ctx.restore()
    
    draw_vehicle(ctx, vehicle, pose)
    
    for i, sensor in enumerate(vehicle.config.sensors):
        mountpoint = vehicle.sensor2mountpoint[sensor]
        sensor_pose = pose.oplus(mountpoint)
        sensor_data = data.all_sensors[i]
            
        if sensor.sensor_type_string() == 'rangefinder':
            draw_rangefinder(ctx, sensor, sensor_pose, sensor_data)
        if sensor.sensor_type_string() == 'optics':
            draw_optics(ctx, sensor, sensor_pose, sensor_data)

    ctx.restore()
    
#    surface.write_to_png('world.png')
    surface.show_page()

if __name__ == '__main__':
    radius = 10
    world = create_random_world(radius)
    rt = TexturedRaytracer()
    rt.set_map(world)
    
    pose = get_safe_pose(rt, world_radius=radius, safe_zone=safe_zone)
    vehicle = Vehicle()
    
    sensor = Rangefinder()
    sensor.add_photoreceptors(linspace(-pi / 2, pi / 2, 45),
                              spatial_sigma=deg2rad(1), sigma=0)
    vehicle.add_sensor(sensor)
    
    sensor = Optics()
    sensor.add_photoreceptors(linspace(-pi / 2, pi / 2, 180),
                              spatial_sigma=deg2rad(1), sigma=0)
    vehicle.add_sensor(sensor)
    
    vehicle.set_map(world)
    data = vehicle.compute_observations(pose)
    simple_drawing(world, vehicle, pose, data)



