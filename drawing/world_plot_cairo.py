''' functions for plotting the world with a cairo context ''' 
from math import pi

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
    
def draw_circle(ctx, object):
    ctx.set_line_width(0.1)
    ctx.set_source_rgb(1, 0, 0)
    center = object['center']
    radius = object['radius']
    ctx.arc(center[0], center[1], radius, 0, 2 * pi)
    ctx.stroke()

def draw_world(ctx, world):
    
    for object in world['objects']:
        if object['class'] == 'polyline':
            draw_polyline(ctx, object)  
        elif object['class'] == 'circle':
            draw_circle(ctx, object)  
        else:
            raise ValueError('Uknown type %s ' % object)
    pass
