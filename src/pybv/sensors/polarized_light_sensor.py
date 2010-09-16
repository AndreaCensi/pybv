from numpy import array, ndarray, linspace, pi, dot, cos, sin
from sensor_interface import Sensor
from pybv.utils import assert_type

class PolarizedLightSensor(Sensor):
    """ This class implements something akin to a polarized sensor
        or a compass. Each sensel is sensitive to a particular direction. """
        
    def __init__(self, num_receptors):
        """
        Initializes the sensor with the given number of receptors
        
        num_receptors: (int >= 1) number of receptors uniformly distributed
                       on the equator 
        
        """
        assert_type(num_receptors, int)
        if num_receptors < 1: 
            raise ValueError('Invalid num_receptors: %s' % num_receptors)
        # Exactly num_receptors uniformly distributed on the 
        self.directions = linspace(0, 2 * pi, num_receptors + 1)[0:-1]

    def num_sensels(self):
        return len(self.directions)

    def sensor_type_string(self):
        return 'polarized'

    def compute_observations(self, sensor_pose_world):
        def versor(angle):
            return array([[cos(angle)], [sin(angle)], [0]])
        
        direction_versor = dot(sensor_pose_world.attitude, versor(0))
        
        response = ndarray(shape=(len(self.directions),))
        for i, theta in enumerate(self.directions):
            response[i] = dot(versor(theta).transpose(), direction_versor)

        return {'sensels': response, 'response': response}

    def set_map(self, map_object):
        # TODO: maybe include sunny, not sunny
        pass
    
    
