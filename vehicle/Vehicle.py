from numpy import array, ndarray
from pybv import BVException
from pybv.utils import OpenStruct, RigidBodyState, assert_1d_ndarray

class Vehicle:
    def __init__(self):
        self.config = OpenStruct() 
        self.config.sensors = []
        self.config.sensor_types = {}
        self.config.num_sensels = 0 
        self.config.num_commands = 0 
        self.dynamics = None
        self.state = RigidBodyState()
        # keep track of the mountpoint for each sensor
        self.sensor2mountpoint = {}
    
    def add_sensor(self, sensor, mountpoint=None):
        if mountpoint is None:
            mountpoint = RigidBodyState()
        self.sensor2mountpoint[sensor] = mountpoint
        self.config.sensors.append(sensor)
        sensor_type = sensor.sensor_type_string()
        if not sensor_type in self.config.sensor_types:
            sensor_array = []
            self.config.sensor_types[sensor_type] = sensor_array
            setattr(self.config, sensor_type, sensor_array)
        self.config.sensor_types[sensor_type].append(sensor)
        self.config.num_sensels += sensor.num_sensels()
        
    def set_map(self, map_object):
        """ Sets the map object for all sensors """
        for sensor in self.config.sensors:
            sensor.set_map(map_object)
        
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
        """ Computes the sensor observations at a certain state.
        
        OK, you might think this function is kind of mysterious
        because of all the introspection we use. However, a little
        black magic here helps in making the client interface
        clear and intuitive.
        
         """
        if vehicle_state is None:
            vehicle_state = self.state
            
        data = OpenStruct()
        data.sensels = []
        
        data.all_sensors = [] 
        for sensor_type in self.config.sensor_types.keys():
            setattr(data, sensor_type, [])
        
        for i, sensor in enumerate(self.config.sensors):
            mountpoint = self.sensor2mountpoint[sensor]
            sensor_pose = vehicle_state.oplus(mountpoint)
            sensor_data = sensor.compute_observations(sensor_pose)
            
            if not 'sensels' in sensor_data:
                raise BVException('Sensor %s did not produce a "sensels" variable' % 
                                  sensor)
            
            for k, v in sensor_data.items():
                if isinstance(v, list):
                    sensor_data[k] = array(v)
            sensor_data = OpenStruct(**sensor_data)

            data_array = getattr(data, sensor.sensor_type_string())
            data_array.append(sensor_data)
            data.all_sensors.append(sensor_data)
            
            # FIXME Look for NAN
            assert_1d_ndarray(sensor_data.sensels)
            data.sensels.extend(list(sensor_data.sensels))

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
        
        # For each sensor type (e.g., sensor_type = 'rangefinder')
        for sensor_type in self.config.sensor_types.keys():
            datas1 = getattr(data1, sensor_type)
            datas2 = getattr(data2, sensor_type)
            # for each sensor output
            for i, data in enumerate(datas1):
                # for each output of the sensor (e.g., obs = 'luminance') 
                for obs in data.__dict__.keys():
                    y1 = datas1[i].__dict__[obs]
                    y2 = datas2[i].__dict__[obs]
                    if not isinstance(y1, ndarray):
                        # ignore spurious members in the response
                        # TODO: make this check more strict
                        continue
                    average = (y1 + y2) / 2.0
                    derivative = (y1 - y2) / dt
                    datas1[i].__dict__[obs] = average
                    datas1[i].__dict__[obs + '_dot'] = derivative
        # finally for all the sensels
        average = (data1.sensels + data2.sensels) / 2
        derivative = (data2.sensels - data1.sensels) / dt
        data1.sensels = average
        data1.sensels_dot = derivative 
        return data1
        
        
    
