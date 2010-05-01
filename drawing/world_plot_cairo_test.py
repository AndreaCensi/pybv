import cairo
from pybv.worlds.world_generation import create_random_world
from pybv.worlds.world_utils import get_safe_pose
from pybv.drawing.world_plot_cairo import draw_world
from pybv.vehicle import Vehicle
from pybv.sensors import Optics
from numpy import pi, linspace, deg2rad, rad2deg, sin, cos
from pybv.sensors.textured_raytracer import TexturedRaytracer
from pybv.sensors.image_range_sensor import Rangefinder

def rototranslate(ctx, pose):
    position = pose.get_2d_position()
    rotation = pose.get_2d_orientation()
    ctx.translate(position[0], position[1])
    ctx.rotate(rotation)

def draw_vehicle(ctx, vehicle, pose):
    ctx.save()
    rototranslate(ctx, pose)
    w, h = 0.4, 0.6
    ctx.rectangle(-w / 2, -h / 2, w, h)
    ctx.set_source_rgb(0, 0, 1)
    ctx.fill()
    ctx.restore()
    
def draw_rangefinder(ctx, sensor, pose, data=None):
    ctx.save()
    rototranslate(ctx, pose)
    
    if data:
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.005)
        for i, theta in enumerate(sensor.directions):
            range = data.readings[i]
            if not range:
                continue
            
            ctx.move_to(0, 0)
            ctx.line_to(cos(theta) * range, sin(theta) * range)
            ctx.stroke()
    
    w, h = 0.3, 0.3
    ctx.rectangle(-w / 2, -h / 2, w, h)
    ctx.set_source_rgb(1, 1, 0)
    ctx.fill()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.005)
    ctx.stroke()
    
    ctx.restore()
    
warned = False
def warn_invalid_lum(lum):
    print "Invalid luminance %f " % lum
    
def draw_optics(ctx, sensor, pose, data=None):
    ctx.save()
    rototranslate(ctx, pose)
    
    if data:
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.005)
        
        range = 2
        for i, theta in enumerate(sensor.directions):
            lum = data.luminance[i]
            if not lum:
                continue
            
            if (lum < 0) or lum > 1:
                warn_invalid_lum(lum)
                lum = 0.5
                
            
            ctx.set_source_rgb(0, lum, lum)
            
            amp = sensor.spatial_sigma[i] * 2
            ctx.move_to(0, 0)
            ctx.arc(0, 0, range, theta - amp, theta + amp)
            #ctx.line_to(cos(theta) * range, sin(theta) * range)
            ctx.fill()
            ctx.stroke()
    
    w, h = 0.2, 0.2
    ctx.rectangle(-w / 2, -h / 2, w, h)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.005)
    ctx.stroke()
    
    ctx.restore()

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
    pose = get_safe_pose(rt, world_radius=radius, safe_zone=0.5)
    vehicle = Vehicle()
    sensor = Optics()
    sensor.add_photoreceptors(linspace(-pi / 2, pi / 2, 180),
                              spatial_sigma=deg2rad(1), sigma=0)
    vehicle.add_sensor(sensor)
    
   # sensor = Rangefinder()
    #sensor.add_photoreceptors(linspace(-pi / 2, pi / 2, 45),
    #                          spatial_sigma=deg2rad(1), sigma=0)
    #vehicle.add_sensor(sensor)
    
    vehicle.set_map(world)
    data = vehicle.compute_observations(pose)
    simple_drawing(world, vehicle, pose, data)



