
from numpy import array, linalg

from pybv.utils import RigidBodyState, assert_type, assert_has_key, ascolumn

# This is necessary to allow arbitrary functions for source strength 
import math, numpy #@UnusedImport
from copy import deepcopy
from pybv.utils.misc import aslist



class OlfactionSensor:
    def __init__(self, normalize_sum=False, normalize_mean=False):
        self.num_receptors = 0
        self.receptors = []
        self.map = None
        self.normalize_sum = normalize_sum
        self.normalize_mean = normalize_mean
        
        
    def sensor_type_string(self):
        return 'olfaction'
    
    def num_sensels(self):
        return self.num_receptors
    
    # pickling: we do not want the lambdas
    def __getstate__(self):
        return {'map': self.map, 'receptors': self.receptors,
                'normalize': self.normalize }
    
    def __setstate__(self, d):
        self.normalize = d['normalize']
        self.receptors = d['receptors']
        self.num_receptors = len(self.receptors)
        if d['map'] is not None:
            self.set_map(d['map'])
        else:
            self.map = None
    
    def set_map(self, world):
        # we will modify "map" throughout
        map = deepcopy(world)
        # also we make a copy for pickling
        self.map = deepcopy(world)

        self.all_chemicals = set()
        self.sources = []

        assert_type(map, dict)        
        sources_key = 'olfaction_sources'
        assert_has_key(map, sources_key)
        sources = map[sources_key]
        assert_type(sources, list)
        for source in sources:
            assert_type(source, dict)
            assert_has_key(source, 'position')
            assert_has_key(source, 'components')
            position = source['position']                
            assert_type(position, list)
            if not len(position) == 3:
                raise ValueError('I expect position with 3 elements, got %s' % position)
            position = array(position)
            components = source['components']
            assert_type(components, dict)
            for chemical, value in components.items():
                assert_type(chemical, str)
                if isinstance(value, str):
                    value = eval(value)
                    components[chemical] = value
                assert_type(value, [int, float, type(lambda x: 0) ]) #@UnusedVariable
                self.all_chemicals.add(chemical)
            if len(components.keys()) == 0:
                raise ValueError('Did you pass me a map without sources? %s' % world)
            
            self.sources.append((position, components))
    
    def add_receptor(self, pose, sensitivity):
        """ Adds a receptor to the sensor.
        
        Args:
            pose: RigidBodyState  pose of the receptor wrt the sensor
            sensitivity:  dict  chemical -> coefficient
        """
        
        # Checking format
        assert_type(pose, RigidBodyState)
        assert_type(sensitivity, dict)
        for key, value in sensitivity.items():
            assert_type(key, str)
            assert_type(value, [int, float, type(lambda x:0) ]) #@UnusedVariable
    
        self.receptors.append((pose, sensitivity))
        self.num_receptors += 1
    
    def compute_smell(self, position):
        """ Compute the smell at a certain position.
        Args: 
            position:  vector in R3 
        
        Returns:
            dictionary { 'chemicalname': value (float) }
        """ 
        def evaluate_effect(effect, distance):
            if isinstance(effect, float) or isinstance(effect, int):
                return effect
            elif isinstance(effect, type(lambda x:0)): # XXX what is a better way to write this? @UnusedVariable
                return effect(distance)
        
        smell = {}
        for chemical in self.all_chemicals:
            smell[chemical] = 0
        
        for source_position, components in self.sources:
            distance = linalg.norm(ascolumn(position) - ascolumn(source_position))
            for chemical, effect_function in components.items():
                effect = evaluate_effect(effect_function, distance)
                smell[chemical] += effect
        return smell
        
    def compute_observations(self, vehicle_pose):
        response = [] 
        # iterate over receptors
        for receptor_pose, sensitivity in self.receptors:
            pose = vehicle_pose.oplus(receptor_pose)
            # compute all the contributions at this position
            smell = self.compute_smell(pose.position)
            total_value = 0
            for chemical, coefficient in sensitivity.items():
                if smell.has_key(chemical):
                    total_value += coefficient * smell[chemical]
            response.append(total_value) 
    
        response = array(response)
        
        if self.normalize_mean:
            response -= response.mean() 
        
        if self.normalize_sum:
            response = response / response.sum() 
    
        return { 'response' : aslist(response), 'sensels': aslist(response) }
        
        
    
