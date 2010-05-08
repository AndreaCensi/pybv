import numpy
from numpy import pi, array, sin, cos
from pybv.worlds.texture_generation import PoissonTexParams, \
    generate_poisson_tex

def generate_texture(scale=1):
    # create arena
    rand_amp = lambda freq: 0.5 * numpy.exp(-0.5 * freq) * numpy.random.rand()
    rand_pha = lambda freq: numpy.random.rand() * 2 * pi
    freqs = [ (freq, rand_amp(freq), rand_pha(freq)) for freq in range(10) ]
     
    s = ' + '.join([' (%f * numpy.cos(%f * (x - %f) ))' % (amp, freq, pha) 
                    for (freq, amp, pha) in freqs  ])  
    texture = 'lambda x: numpy.minimum(1, numpy.maximum( %s, 0 ))' % s
    
    assert eval(texture), 'Did not create a good texture string: %s' % texture
    #print texture
    return texture

def generate_poisson_texture(length):
    cell_size = 0.01
    intensity = 5.0
    sigma = (1.0 / intensity) * 3
    seed = 0
    params = PoissonTexParams(seed, length, cell_size, sigma, intensity)
    texture = generate_poisson_tex(params)
    return texture
    

def create_random_world(radius, num_lines=10, num_circles=5):
    objects = []
    
    def random_point():
        return (numpy.random.rand(2) - 0.5) * 2 * radius 
    
    # texture = generate_texture()
    #objects.append(
    #    { "class": "circle", "surface": 0, "radius": radius, "center": [0.0, 0.0],
    #     "texture": texture, "solid_inside": 0}
    #)
    
    #texture = "lambda s:  numpy.mod(s,10)/10"
    w = radius - 0.1
    texture = generate_poisson_texture(length=w * 2 * 4)
    if 1:
        objects.append(
            { 
             "class": "polyline", "surface": 0,
             "texture": texture,
             "points": [ [-w, -w], [w, -w], [w, w], [-w, w], [-w, -w]]
             }
        )
        
    
    average_length = radius / 3.0
    
    for x in range(num_lines):
        p1 = random_point()
        length = float(average_length * (1 + 0.3 * numpy.random.rand(1)))
        theta = float(numpy.random.rand(1) * 2 * pi)
        
        diff = array([cos(theta) * length, sin(theta) * length])
        p2 = p1 + diff
        #texture = generate_texture()
        texture = generate_poisson_texture(length=length)
        # XXX add check in raytracer
        object = { "class": "polyline", "surface": x + 2000,
                         "points": [list(p1), list(p2)], "texture": texture}
        objects.append(object)

    
    random_radius = lambda : 2 + 2 * numpy.random.rand(1)
    for x in range(num_circles):
        center = random_point()
        circle_radius = random_radius()
        # texture = generate_texture()
        texture = generate_poisson_texture(length=2 * pi * circle_radius)
      #  texture = "lambda s: numpy.mod(s,8)/8"
        objects.append({ "class": "circle", "surface": x + 1000,
                        "radius": float(circle_radius),
                        "center": list(center),
         "texture": texture, "solid_inside": 0}
                       )
    
        


    olfaction_sources = []    
    num_sources = 10
    for x in range(num_sources):
        position = list(radius * 2 * (numpy.random.rand(2) - 0.5))
        position.append(1)
        scale = numpy.random.rand(1) * 1
        dist_func = "lambda dist: math.exp(- dist / %f ) " % scale
        olfaction_sources.append({  "position": position, 'components':
                                   { 'food': dist_func } })
        
    world = {"class": "map", "objects": objects,
              "olfaction_sources": olfaction_sources}
    
    return world 
