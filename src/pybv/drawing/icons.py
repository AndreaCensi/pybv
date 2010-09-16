''' This module contains functions to draw icons for the vehicles.
    These icons are suitable for presentation in a paper. '''
import cairo
from pybv.drawing.world_plot_cairo import draw_vehicle
from pybv.utils.rigid_body_state import RigidBodyState
from pybv.drawing.world_plot_cairo import rototranslate
from numpy import deg2rad,cos,sin 
import numpy

def rounded_rectangle(context,x,y,w,h,r = 10):
    "Draw a rounded rectangle"
    #   A****BQ
    #  H      C
    #  *      *
    #  G      D
    #   F****E

    context.move_to(x+r,y)                      # Move to A
    context.line_to(x+w-r,y)                    # Straight line to B
    context.curve_to(x+w,y,x+w,y,x+w,y+r)       # Curve to C, Control points are both at Q
    context.line_to(x+w,y+h-r)                  # Move to D
    context.curve_to(x+w,y+h,x+w,y+h,x+w-r,y+h) # Curve to E
    context.line_to(x+r,y+h)                    # Line to F
    context.curve_to(x,y+h,x,y+h,x,y+h-r)       # Curve to G
    context.line_to(x,y+r)                      # Line to H
    context.curve_to(x,y,x,y,x+r,y)             # Curve to A
    return

def draw_circle(ctx,x,y,r,fill=(1,1,1),border=(0,0,0),border_width=0.1):
    ctx.save()
    if fill is not None:
        ctx.arc(x,y,r,0,numpy.pi*2)
        ctx.set_source_rgb(*fill)
        ctx.fill()

    if border is not None:
        ctx.arc(x,y,r,0,numpy.pi*2)
        ctx.set_source_rgb(*border)
        ctx.set_line_width(border_width)
        ctx.stroke()
    ctx.restore()

def draw_rectangle(ctx,w,h,x=0,y=0,fill=(1,1,1),border=(0,0,0),border_width=0.1):
    ctx.save()
    if fill is not None:
        ctx.rectangle(x-w/2,y-h/2,w,h)
        ctx.set_source_rgb(*fill)
        ctx.fill()

    if border is not None:
        ctx.rectangle(x-w/2,y-h/2,w,h)
        ctx.set_source_rgb(*border)
        ctx.set_line_width(border_width)
        ctx.stroke()
    ctx.restore()

def draw_rounded_rectangle(ctx,w,h,r,x=0,y=0,fill=(1,1,1),border=(0,0,0),border_width=0.1):
    ctx.save()
    if fill is not None:
        rounded_rectangle(ctx,x-w/2,y-h/2,w,h,r)
        ctx.set_source_rgb(*fill)
        ctx.fill()

    if border is not None:
        rounded_rectangle(ctx,x-w/2,y-h/2,w,h,r)
        ctx.set_source_rgb(*border)
        ctx.set_line_width(border_width)
        ctx.stroke()
    ctx.restore()

def draw_vehicle_icon(vehicle, filename, width=6000,height=6000):
    ''' Creates a pdf file (filename) for the vehicle icon.
    
    Arguments
    ---------
    
    width, height:  size in points of PDF figure
    
    '''
   
    # surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, width, height)
    surface = cairo.PDFSurface(filename, width, height)
    ctx = cairo.Context(surface)
    
    # creates a [-box,+box] x [-box,+box]
    box = 0.45
    ctx.save()
    ctx.translate(width / 2, height / 2)
    ctx.scale(0.5 * width / box, 0.5 * height / box)
    ctx.scale(1, -1)
    ctx.rectangle(-box, -box, 2 * box, 2 * box)
    #ctx.set_source_rgb(0, 1, 0)
    #ctx.stroke()
    ctx.clip() 
    
    
    if 0:
        rw,rh = 0.5,0.6
        # wheels (unicycle)
        for x,y in [(-rw/2,0), (+rw/2,0), (0, rh/2)]:
            draw_rounded_rectangle(ctx, w=0.1,h=0.2,r=0.02,
                                   x=x,y=y,fill=(0.5,0.5,0.5), 
                       border=(0,0,0), border_width=0.02)
        # body
        draw_rounded_rectangle(ctx, w=rw,h=rh,r=0.05,fill=(1,1,1), 
                       border=(0,0,0), border_width=0.02)

    # omnidirectional
    if 1:
        rw,rh = 0.5,0.5

        # wheels (unicycle)
        for theta in [0,120,240]:
            ctx.save()
            ctx.rotate(deg2rad(theta))
            draw_rounded_rectangle(ctx, h=0.1,w=0.2,r=0.02,
                                   y=0,x=rw/2,fill=(0.5,0.5,0.5), 
                       border=(0,0,0), border_width=0.02)
            ctx.restore()
            
        # body
        ctx.arc(0,0,rw/2,0,numpy.pi*2)
        ctx.set_source_rgb(1,1,1)
        ctx.fill()
        ctx.arc(0,0,rw/2,0,numpy.pi*2)
        ctx.set_source_rgb(0,0,0)
        ctx.set_line_width(0.02)
        ctx.stroke()
        
        ctx.move_to(0, 0)
        ctx.line_to(rw/2,0)
        ctx.set_source_rgb(0,0,0)
        ctx.set_line_width(0.02)
        ctx.stroke()
              

    pose = RigidBodyState([0,0],0)
    #draw_vehicle(ctx, vehicle, pose)
    
    for i, sensor in enumerate(vehicle.config.sensors):
        mountpoint = vehicle.sensor2mountpoint[sensor]
        sensor_pose = pose.oplus(mountpoint)
        ctx.save()
        rototranslate(ctx, sensor_pose)
        
        if sensor.sensor_type_string() == 'rangefinder':
                
            draw_rectangle(ctx, w=0.2,h=0.2,fill=(1,1,0), 
                   border=(0,0,0), border_width=0.01)

            ctx.set_source_rgba(1, 0, 0,0.7)
            ctx.set_line_width(0.005)
            for theta in sensor.directions:
                range = 0.7 * (0.36 + 0.03 * sin(10*theta))
                ctx.move_to(0, 0)
                ctx.line_to(cos(theta) * range, sin(theta) * range)
                ctx.stroke()
                
            draw_circle(ctx,x=0,y=0,r=0.025,fill=(0,0,0),border=(0,0,0),
                        border_width=0.01)
                

        elif sensor.sensor_type_string() == 'optics':
            
            ctx.set_line_width(0.005)
            for theta in sensor.directions:
                ctx.set_source_rgba(0, abs(cos(2*theta)), 1-abs(cos(2*theta)),0.7)
                range = 0.2
                ctx.move_to(0, 0)
                ctx.line_to(cos(theta) * range, sin(theta) * range)
                ctx.stroke()
            
            draw_rectangle(ctx, w=0.1,h=0.1,fill=(0.6,0.6,0.6), 
                   border=(0,0,0), border_width=0.01)

        elif sensor.sensor_type_string() == 'olfaction':
            i = 0
            for receptor_pose, sens in sensor.receptors: #@UnusedVariable
                ctx.save()
                scale = 0.4
                ctx.scale(scale,scale)
                rototranslate(ctx, receptor_pose)
                ctx.scale(1/scale,1/scale)
                c = abs(cos(0.2*i))
                col = (c,1-c,0)
                draw_circle(ctx,x=0,y=0,r=0.015,fill=col,border=(0,0,0),
                        border_width=0.005)
                ctx.restore()
                i += 1
                
        elif sensor.sensor_type_string() == 'polarized':
                        
            range = 0.1
            for i in xrange(len(sensor.directions)):
                theta1 = sensor.directions[i-1]
                theta2 = sensor.directions[i]
                
                ctx.set_line_width(0.005)
                ctx.set_source_rgba(0, 0, 1-abs(cos(2*theta2)),0.7)
                ctx.move_to(0, 0)
                ctx.arc(0,0,range,theta1,theta2)
                ctx.fill()
         
            ctx.arc(0,0,range,0,numpy.pi*2)
            ctx.set_source_rgba(0, 0, 0,1)
            ctx.stroke()
#        
#            ctx.move_to(0, 0)
#            ctx.line_to(cos(theta1) * range, sin(theta1) * range)
#            ctx.set_source_rgba(0, 0, 0,1)
#            ctx.stroke()
#        
        else:
            print "not drawing %s"  %  sensor.sensor_type_string()
#            draw_rangefinder(ctx, sensor, sensor_pose, sensor_data)
#        if sensor.sensor_type_string() == 'optics':
#            draw_optics(ctx, sensor, sensor_pose, sensor_data)

        ctx.restore()
        
    ctx.restore()

    surface.show_page()
