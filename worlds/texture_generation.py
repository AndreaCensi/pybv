from collections import namedtuple
from numpy.random import exponential
from numpy import zeros, convolve, array
from pybv.utils.numpy_utils import require_shape, gt
from numpy.lib.function_base import linspace
import numpy
import pylab
from numpy.ma.core import ceil
import time
from pybv.worlds.texture import Texture


PoissonTexParams = \
     namedtuple('PoissonTexParams',
                'seed, length, cell_size, smoothing_sigma, intensity')

def generate_poisson_events(intensity, length):
    assert intensity > 0
    assert length > 0
    time = 0
    events = [0]
    while True:
        time += exponential(1.0 / intensity)
        if time > length:
            break
        events.append(time)
    return events

def loop_convolve(x, filter):
    ''' Wraps around x and convolves with the filter '''
    require_shape((gt(0),), x)
    n = x.shape[0]
    a = zeros(shape=3 * n) 
    a[0:n] = x
    a[n:(2 * n)] = x
    a[2 * n:(3 * n)] = x
    af = convolve(a, filter, mode='same')
    require_shape((3 * n,), af)
    result = af[(n):(2 * n)]
    return result


def generate_poisson_tex(params):
    seed = params.seed
    # TODO: select seed 
    length = params.length
    cell_size = params.cell_size
    sigma = params.smoothing_sigma
    intensity = params.intensity
    
    buffer_len = int(ceil(length / cell_size))
    cell_size = (1.0 * length) / buffer_len
    buffer = zeros(shape=(buffer_len,))
    
    def generate_inverted_colors_sequence(length):
        colors = zeros(shape=(length,)) 
        for i in range(length):
            colors[i] = i % 2
        return colors
    def generate_random_colors_sequence(length):
        return numpy.random.rand(length)
    
    events = generate_poisson_events(intensity, length)
    colors = generate_random_colors_sequence(len(events))
     
    current_event = 0
    for i in xrange(buffer_len):
        current_time = i * cell_size
        if current_event < len(events) - 1 and current_time > events[current_event]: # XXX
            current_event += 1
            
        buffer[i] = colors[current_event] 
    
    tail = 4 * sigma
    gaussian_filter_len = int(ceil(tail / cell_size)) 
    xcoord = linspace(-tail, tail, gaussian_filter_len)
    gaussian_filter = numpy.exp(-xcoord ** 2 / (2 * sigma ** 2))
    gaussian_filter = gaussian_filter / gaussian_filter.sum() 
    
    buffer = loop_convolve(buffer, gaussian_filter)
    
    return Texture(buffer=buffer, cell_size=cell_size)
    

if __name__ == '__main__':
    seed = 0
    length = 10
    cell_size = 0.01
    intensity = 5.0
    sigma = (1.0 / intensity) * 2
    params = PoissonTexParams(seed, length, cell_size, sigma, intensity)
    
    pylab.figure()
    for n in range(10):
        texture = generate_poisson_tex(params)
        x = array(range(len(texture.buffer))) * texture.cell_size
        #pylab.plot(x, texture.buffer)
        im = numpy.tile(texture.buffer, (200, 1))
        pylab.imshow(im, cmap=pylab.cm.gray) #@UndefinedVariable
        pylab.show()
        #time.sleep(5)
    pylab.show()
