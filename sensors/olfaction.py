from numpy import array, linalg
from pybv.utils import RigidBodyState, assert_type, assert_has_key, ascolumn

# This is necessary to allow arbitrary functions for source strength 
import math, numpy


class OlfactionSensor:
    def __init__(self):
        self.num_photoreceptors = 0
        self.receptors = []
        
        self.sources = []
        self.all_chemicals = set()
    
    def set_map(self, map):
        assert_type(map, dict)        
        sources_key = 'olfaction_sources'
        assert_has_key(map, sources_key)
        sources = map[sources_key]
        assert_type(sources, list)
        for source in sources:
            assert_type(source,dict)
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
                assert_type(value, [int, float, type(lambda x:0) ])
                self.all_chemicals.add(chemical)
            if len(components.keys()) == 0:
                raise ValueError('Did you pass me a map without sources? %s' % map)
            
            self.sources.append((position, components))
    
    def add_receptor(self, pose, sensitivity):
        """ Adds a receptor to the sensor.
        
        Args:
            pose: RigidBodyState  pose of the receptor wrt the sensor
            sensitivity:  dict  chemical -> coefficient
        """
        
        # Checking format
        assert_type(pose, RigidBodyState)
        assert_type(sensitivity, dict )
        for key, value in sensitivity.items():
           assert_type(key, str)
           assert_type(value, [int, float, type(lambda x:0) ])
    
        self.receptors.append( (pose, sensitivity) )
    
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
            elif isinstance(effect, type(lambda x:0)): # XXX what is a better way to write this?
                return effect(distance)
        
        smell = {}
        for chemical in self.all_chemicals:
            smell[chemical] = 0
        
        for source_position, components in self.sources:
            distance = linalg.norm( ascolumn(position) - ascolumn(source_position) )
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
                total_value += coefficient * smell[chemical]
            response.append(total_value) 
    
        return { 'response' : response }
        
        
    