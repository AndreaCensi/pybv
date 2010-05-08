''' functions for plotting the world with a cairo context ''' 

from numpy import pi, linspace, cos, sin
import numpy

from numpy import array, isnan

def draw_polyline(ctx, object):
    points = object['points']
    
    ctx.set_line_width(0.1)
    ctx.set_source_rgb(0, 0, 0)
    
    for i, p in enumerate(points):
        if not i:
            ctx.move_to(p[0], p[1])
        else:
            ctx.line_to(p[0], p[1])
    
    ctx.stroke() 
    
    texture = object['texture']
    if isinstance(texture, str):
        texture = eval(texture) 
    
    current_coord = 0
    for i in range(len(points) - 1):
        interval = 0.1
        p0 = array(points[i])
        p1 = array(points[i + 1])
        length = numpy.linalg.norm(p1 - p0)
        num_blobs = length / interval
        ss = linspace(0, length, num_blobs)
        for s in ss:
            point = p0 + (p1 - p0) * (s / length)
            lum = texture(current_coord + s)
            ctx.set_source_rgb(lum, lum, lum)
            ctx.arc(point[0], point[1], interval, 0, 2 * pi)
            ctx.fill() 
        current_coord += length
        
def draw_circle(ctx, object):
    ctx.set_line_width(0.1)
    ctx.set_source_rgb(1, 0, 0)
    center = object['center']
    radius = object['radius']
    ctx.arc(center[0], center[1], radius, 0, 2 * pi)
    ctx.stroke()
    
    # TODO: put this logic somewhere else
    texture = object['texture']
    if isinstance(texture, str):
        texture = eval(texture) 
         
    
    
    
    interval = 0.1
    perimeter = 2 * pi * radius
    num_blobs = perimeter / interval
    angles = linspace(0, 2 * pi, num_blobs)
    for theta in angles:
        s = theta * radius
        lum = texture(s)
        x = radius * cos(theta) + center[0]
        y = radius * sin(theta) + center[1]
        ctx.set_source_rgb(lum, lum, lum)
        ctx.arc(x, y, interval, 0, 2 * pi)
        ctx.fill()

def draw_world(ctx, world):
    
    for object in world['objects']:
        if object['class'] == 'polyline':
            draw_polyline(ctx, object)  
        elif object['class'] == 'circle':
            draw_circle(ctx, object)  
        else:
            raise ValueError('Uknown type %s ' % object)

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
    
    print data.readings
    if data:
        ctx.set_source_rgb(1, 0, 0)
        ctx.set_line_width(0.005)
        for i, theta in enumerate(sensor.directions):
            range = data.readings[i]
            if isnan(range):
                continue
            
            ctx.move_to(0, 0)
            ctx.line_to(cos(theta) * range, sin(theta) * range)
            ctx.stroke()
    
    w, h = 0.3, 0.3
    ctx.rectangle(-w / 2, -h / 2, w, h)
    ctx.set_source_rgb(1, 1, 0)
    ctx.fill()
    ctx.rectangle(-w / 2, -h / 2, w, h)
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.01)
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
        luminance = array(data.luminance)
        for i, theta in enumerate(sensor.directions):
            lum = data.luminance[i]
            if isnan(lum):
                continue
            
            if (lum < 0) or lum > 1:
                warn_invalid_lum(lum)
                lum = 0.5
                
            ctx.set_source_rgb(lum, lum, lum)
            
            #amp = sensor.spatial_sigma[i] * 2
            if i > 2:
                amp = sensor.directions[i] - sensor.directions[i - 1]
            elif i < len(sensor.directions) - 1:
                amp = sensor.directions[i + 1] - sensor.directions[i]
            amp = amp / 2
            ctx.move_to(0, 0)
            ctx.arc(0, 0, range, theta - amp, theta + amp)
            #ctx.line_to(cos(theta) * range, sin(theta) * range)
            ctx.fill()
            ctx.stroke()
        ctx.arc(0, 0, range, sensor.directions[0], sensor.directions[-1])
        ctx.set_source_rgb(0.5, 1, 1)
        ctx.stroke()
        
    w, h = 0.2, 0.2
    ctx.rectangle(-w / 2, -h / 2, w, h)
    ctx.set_source_rgb(0, 0, 0)
    ctx.fill()
    ctx.set_source_rgb(0, 0, 0)
    ctx.set_line_width(0.005)
    ctx.stroke()
    
    ctx.restore()
