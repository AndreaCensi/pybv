from numpy import ceil, rad2deg, linspace, array
from textured_raytracer import TexturedRaytracer

class ImageRangeSensor(TexturedRaytracer):
    def __init__(self, world=None):
        TexturedRaytracer.__init__(self)
        self.directions = []
        self.spatial_sigma = []
        self.sigma = []
        if world is not None:
            self.set_map(world)
            
        self.compiled = False
        
    def make_sure_compiled(self):
        """ We finished composing the sensor """
        if not self.compiled:
            self.set_sensor(self.get_raw_sensor())
            self.compiled = True
        
    def add_photoreceptors(self, directions, spatial_sigma, sigma):
        n = len(directions)
        
        if not isinstance(spatial_sigma, list):
            spatial_sigma = [spatial_sigma] * n
        if not isinstance(sigma, list):
            sigma =   [sigma] * n
        
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
        
    def get_raw_sensor(self):
        min_num_aux = 3
        aux_per_deg = 1
        # list of list of indices
        self.aux_indices = []
        self.aux_directions = []
        for i, direction in enumerate(self.directions):
            spatial_sigma = self.spatial_sigma[i] 
            
            num_aux = int(max(ceil(rad2deg(spatial_sigma/aux_per_deg)), min_num_aux)) 
            # enforce odd to have a centered ray
            if num_aux % 2 == 0: 
                num_aux += 1
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
            aux_values = array(data[attribute])
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
        
    def render(self, object_state):
        self.make_sure_compiled()
        position = object_state.get_2d_position()
        orientation = object_state.get_2d_orientation()
        query = {"class":"query",
            "position": [position[0,0], position[1,0]], 
            "orientation": orientation}
        raw_data = self.query(query)
        proc_data = self.process_raw_data(raw_data)
        return proc_data
        
        
        