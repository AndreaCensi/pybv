from numpy import ceil, rad2deg, linspace, array
from textured_raytracer import TexturedRaytracer
from pybv import BVException

class ImageRangeSensor(TexturedRaytracer):
    def __init__(self, raytracer='raytracer2', world=None, min_num_aux=1, aux_per_deg=1):
        TexturedRaytracer.__init__(self,raytracer=raytracer)
        self.directions = []
        self.spatial_sigma = []
        self.sigma = []
        self.num_photoreceptors = 0
        if world is not None:
            self.set_map(world)
        
        self.min_num_aux = min_num_aux
        self.aux_per_deg = aux_per_deg
        
        # these are filled in by get_raw_sensor()
        self.compiled = False
        self.aux_directions = None
        self.aux_indices = None
        
    
    def render(self, object_state):
        self.make_sure_compiled()
        position = object_state.get_2d_position()
        orientation = object_state.get_2d_orientation()
        raw_data = self.query_sensor(position, orientation)
        proc_data = self.process_raw_data(raw_data)
        return proc_data
  
    def add_photoreceptors(self, directions, spatial_sigma, sigma):
        n = len(directions)
        
        if not isinstance(spatial_sigma, list):
            spatial_sigma = [spatial_sigma] * n
        if not isinstance(sigma, list):
            sigma = [sigma] * n
        
        self.directions.extend(directions)
        self.spatial_sigma.extend(spatial_sigma)
        self.sigma.extend(sigma)
        
        # re-order everything according to direction
        def permutation_indices(data):
             return sorted(range(len(data)), key = data.__getitem__)
        
        self.indices = permutation_indices(self.directions)
        self.directions    = [self.directions[i]    for i in self.indices]
        self.spatial_sigma = [self.spatial_sigma[i] for i in self.indices]
        self.sigma         = [self.sigma[i]         for i in self.indices]
        
        self.num_photoreceptors = len(self.directions)
        self.num_readings = len(self.directions)
        
        # force reconfiguration of raw sensor
        self.compiled = False
        
    def make_sure_compiled(self):
        """ We finished composing the sensor """
        if not self.compiled:
            if len(self.directions) == 0:
                raise BVException('You did not specify any receptors for the sensor.')
            self.set_sensor(self.get_raw_sensor())
            self.compiled = True
        
    def get_raw_sensor(self):
        # list of list of indices
        self.aux_indices = []
        self.aux_directions = []
        for i, direction in enumerate(self.directions):
            spatial_sigma = self.spatial_sigma[i] 
            
            num_aux = int(max(ceil(rad2deg(spatial_sigma/self.aux_per_deg)), self.min_num_aux)) 
            # enforce odd to have a centered ray
            if num_aux % 2 == 0: 
                num_aux += 1
            if num_aux == 1:
                aux_dirs = [direction]
                # special case: linspace(a,b,1) == a
            else:
                aux_dirs = linspace( -spatial_sigma + direction, +spatial_sigma + direction, num_aux)
            num_so_far = len(self.aux_directions)
            self.aux_directions.extend(aux_dirs)
            self.aux_indices.append(range(num_so_far, num_so_far+num_aux))
        
        return {'class': 'sensor', 'directions': self.aux_directions }
        
    def process_raw_data(self, data):
        # example {"luminance": [1.0, -1.0, -1.0, -1.0, 1.0], "normal": [1.5707960000000001, 3.1415929999999999, 0.0, 3.1415929999999999, 4.7123889999999999], "region": [0, 0, 0, 0, 0], "surface": [0, 0, 0, 0, 0], "readings": [1.0, 1.406641, 1.0, 1.406641, 1.0], "valid": [1, 1, 1, 1, 1], "curvilinear_coordinate": [6.9992039999999998, 5.9892620000000001, 5.0, 4.0107379999999999, 3.0007959999999998]}
        proc_data = {}
        aux_valid = data['valid']
        valid = []
        for attribute in ['luminance', 'readings']:
            values = []
            try:
                aux_values = array(data[attribute])
            except ValueError, e:
                print attribute, data[attribute]
                raise e
                
            for i, indices in enumerate(self.aux_indices):
                valid_indices = [ k for k in indices if aux_valid[k] ]
                if len(valid_indices) == 0:
                    values.append(float('nan'))
                    valid.append(0)
                else:
                    average = aux_values[valid_indices].mean()
                    values.append(average)
                    valid.append(1)
                    
            proc_data[attribute] = values
        
        proc_data['valid'] = valid
        return proc_data
        
        
        