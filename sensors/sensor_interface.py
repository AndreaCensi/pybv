
class Sensor:
    """ This class encapsulates the idea of a vehicle's sensor. 
    Note that Sensor classes do not have to inherit from this (duck typing)
    However this class shows what is the expected interface. 
    """
    def sensor_type_string(self):
        """ Each sensor has friendly 'sensor_type' string ('rangefinder','polarizer','optics',...) """
        raise TypeError('Sensor class %s must implement sensor_type_string()' % type(self) ) 

    def num_sensels(self):
        """ Returns the number of sensels for the sensor. """
        raise TypeError('Sensor class %s must implement num_sensels()' % type(self) )
 
    def compute_observations(self, sensor_pose_world):
        """ Computes the observations for this vehicle         
        Args: 
            sensor_pose_world (RigidBodyState): pose/velocity of the sensor in a
                the world reference frame.
            
        Returns: 
            a dictionary, containing as many data fields as desired. This data
            is eventually passed to the client as a OpenStruct.
            
            There is, however, one necessary field.
            * data['sensels'] should be the declared sensel for the sensor.
              This should be a numpy.ndarray, or a list of numbers.
              No NANs allowed.
            * data['normalized_sensels'] is a mapping of the sensels to [-1, +1]. 
        """
        raise TypeError('Sensor class %s must implement compute_observations()' % type(self) )
    
    def set_map(self, map_object):
        """ Sensors can be passed a map of the environment. See the documentation
            for the format of this object. """
        pass
    
    