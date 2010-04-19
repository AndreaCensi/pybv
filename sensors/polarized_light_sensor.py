from numpy import array
from sensor_interface import Sensor
from pybv.utils import assert_type 

class PolarizedLightSensor(Sensor):
    """ This class implements something akin to a polarized sensor
        or a compass. Each sensel is sensitive to a particular direction. """
    def __init__(self, num_receptors):
        assert_type(num_receptors, int)
        # Exactly num_receptors uniformly distributed on the 
        self.directions = linspace(0, 2*math.pi, num_receptors+1)[0,-1]

    def sensor_type_string(self):
        return 'polarized'

    def obtain_observations(self, sensor_pose_world):
        direction_versor = dot(sensor_pose_world.attitude, array([[1],[0],[0]]))
        response = map( 
            lambda theta:  dot(direction_versor, array([cos(theta), sin(theta)]) ), 
            self.directions  )
        return {'sensels': response, 'response': response}

    def set_map(self, map_object):
        # TODO: maybe include sunny, not sunny
        pass