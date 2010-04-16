from pybv.utils import OpenStruct, RigidBodyState
from numpy import array

class Vehicle:
    def __init__(self):
        self.config = OpenStruct()
        self.config.optics = []
        self.config.rangefinder = []
        self.config.num_sensels = 0 
        self.config.num_commands = 0 
        
        self.dynamics = None
        self.state = RigidBodyState()
        
    def add_optic_sensor(self, sensor, mountpoint=RigidBodyState()):
        # FIXME add mountpoint 
        self.config.optics.append(sensor)
        self.config.num_sensels += sensor.num_photoreceptors
    
    def add_rangefinder(self, sensor, mountpoint=RigidBodyState()):
        # FIXME add mountpoint 
        self.config.rangefinder.append(sensor)
        self.config.num_sensels += sensor.num_readings
        
    def set_dynamics(self, dynamics):
        self.dynamics = dynamics
        if dynamics is not None:
            self.config.num_commands = len(dynamics.commands)
        else:
            self.config.num_commands = 0
        
    def set_controller(self, controller):
        self.config.controller = controller
        
    def set_state(self, state):
        if not isinstance(state, RigidBodyState):
            raise TypeError('Expected RigidBodyState instead of %s' % type(state))
        self.state = state

    def compute_observations(self, vehicle_state=None):
        """ Computes the sensor observations at a certain state """
        if vehicle_state is None:
            vehicle_state = self.state
            
        data = OpenStruct()
        data.sensels = []
        
        data.optics = []
        for i, sensor in enumerate(self.config.optics):
            # FIXME add translation from base pose
            sensor_pose = vehicle_state
            sensor_data = sensor.render(sensor_pose)
            sensor_data = OpenStruct(**sensor_data)
            sensor_data.luminance = array( sensor_data.luminance )
            data.optics.append( sensor_data )
            # FIXME Look for NAN
            data.sensels.extend(sensor_data.luminance)

        data.rangefinder = []
        for i, sensor in enumerate(self.config.rangefinder):
            # FIXME add translation
            sensor_pose = vehicle_state
            sensor_data = sensor.render(sensor_pose)
            sensor_data = OpenStruct(**sensor_data)
            sensor_data.readings = array(sensor_data.readings)
            data.rangefinder.append( sensor_data )
            data.sensels.extend( sensor_data.readings )

        data.sensels = array(data.sensels)
        
        return data

    def compute_observations_and_derivatives(self, state1, state2, dt):
        """ Computes the sensor observations and their derivatives, 
            at the two states state1 and state2. 
            
            This function calls, in turn, ``compute_observations()``
            and computes the variation of the observations from state1 to state2.
             
            Args:
                state1 (RigidBodyState):  first state  
                state2 (RigidBodyState):  second state  
                dt     (float):           time elapsed  
                
            Returns:
                OpenStruct. The same structure returned by ``compute_observations()``
                but with some members added (``luminance_dot``, ``readings_dot``, 
                ``sensels_dot``).
                
        """        
        data1 = self.compute_observations(state1)
        data2 = self.compute_observations(state2)
        
#        print state1,state2
#        print "data1", data1.sensels[0:5]
#        print "data2", data2.sensels[0:5]
        
        for i, data in enumerate(data1.optics):
            average    = (data1.optics[i].luminance + data2.optics[i].luminance)/2
            derivative = (data2.optics[i].luminance - data1.optics[i].luminance)/dt
            data1.optics[i].luminance = average
            data1.optics[i].luminance_dot = derivative
            
        for i, data in enumerate(data1.rangefinder):
            average    = (data1.rangefinder[i].readings + data2.rangefinder[i].readings)/2
            derivative = (data2.rangefinder[i].readings - data1.rangefinder[i].readings)/dt
            data1.rangefinder[i].readings = average
            data1.rangefinder[i].readings_dot = derivative

        
        average = (data1.sensels + data2.sensels)/2
        derivative = (data2.sensels - data1.sensels)/dt
        data1.sensels = average
        data1.sensels_dot = derivative
        
#        print "data1.dot", data1.sensels_dot
        
        return data1
        
        
    