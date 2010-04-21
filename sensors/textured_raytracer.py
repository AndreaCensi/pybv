import sys, errno
from copy import deepcopy
import simplejson
from jsonstream import JSONStream
from subprocess import Popen, PIPE
# Mainly because we want to use user-defined textures
from numpy import *

from pybv.utils import aslist, asscalar, assert_type, assert_has_key
from pybv import BVException


class TexturedRaytracer:
    def __init__(self, raytracer='raytracer2'):
        self.init_connection(raytracer)
        self.surface2texture = {}
        self.map = None
        self.sensor_desc = None

    def init_connection(self, raytracer):
        self.raytracer = raytracer
        try:
            self.p = Popen(raytracer, stdout=PIPE, stdin=PIPE)
            self.child_stream = JSONStream(self.p.stdout)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise BVException('Could not open connection to raytracer ("%s"). Reason: %s.' % (raytracer, e.strerror))
            raise e

    # pickling
    def __getstate__(self):
        return {'map': self.map, 
                'raytracer': self.raytracer, 
                'sensor_desc':self.sensor_desc}
    def __setstate__(self, d):
        self.surface2texture={}
        self.init_connection(d['raytracer'])
        if d['map'] is not None:
            self.set_map(d['map'])
        else:
            self.map = None
        if d['sensor_desc'] is not None:
            self.set_sensor(d['sensor_desc'])
        else:
            self.sensor_desc = None
        
    def set_map(self, map_object):
        if not isinstance(map_object, dict):
            raise TypeError('Expected dict instead of %s' % type(map_object))
        if not 'objects' in map_object:
            raise BVException('Expected map_object["objects"]; available keys are %s' % map_object.keys())
            
        # get a copy (because later we remove 'texture')
        map_object = deepcopy(map_object)

        self.map = map_object

        assert_has_key(map_object, 'objects')
        objects = map_object['objects']
        assert_type(objects, list)
        for object in objects:
            assert_type(object, dict)
            if object.has_key('texture'):
                texture = object.get('texture')
                # del object['texture']
            else:
                # FIXME make this configurable
                raise ValueError('texture not provided for object %s' % object)
#                texture = lambda x: 0.5
            if isinstance(texture, str):
                texture = eval( texture) 
                
            surface = object['surface']
            self.surface2texture[surface] = texture
        
#        sys.stderr.write("Textures: %s\n" % self.surface2texture)
#        print map_object
        simplejson.dump(map_object, self.p.stdin)
        self.p.stdin.write('\n') 
        
    def query_sensor(self, position, orientation):
        if self.map is None:
            raise BVException('Sensor queried before map was defined.')
        if self.sensor_desc is None:
            raise BVException('Sensor queried before sensor was defined.')
            
        position = aslist(position)
        orientation = asscalar(orientation)
        query_object = {"class": "query_sensor",
            "position": [position[0], position[1]], 
            "orientation": orientation}
        
        simplejson.dump(query_object, self.p.stdin)
        self.p.stdin.write('\n')
        
        answer = self.child_stream.read_next()
        if answer is None:
            raise Exception, "Could not communicate with child"
        
        luminance = []
        for i, surface_id in enumerate(answer['surface']):
            if answer['valid'][i]:
                texture = self.surface2texture[surface_id]
                coord = answer['curvilinear_coordinate'][i]
                luminance.append( asscalar(texture(coord))  )
            else:
                luminance.append( float('nan')  )
        
        answer['luminance'] = luminance
        
        return answer
        
    def set_sensor(self, sensor_desc):
        self.sensor_desc = sensor_desc
        simplejson.dump(sensor_desc, self.p.stdin)
        self.p.stdin.write('\n') 
        
    def query_circle(self, center, radius):
        if self.map is None:
            raise BVException('query_circle called before map was defined.')
        
        center = aslist(center)
        radius = asscalar(radius)
        """ Returns tuple (hit, surface_id) """
        query_object = {"class": "query_circle",
            "center": [ center[0], center[1] ], 
            "radius": radius}    
        simplejson.dump(query_object, self.p.stdin)
        self.p.stdin.write('\n')
        
        answer = self.child_stream.read_next()
        if answer is None:
                raise BVException, "Could not communicate with child"
        assert( answer['class'] == "query_circle_response" )
        
        hit = answer['intersects']
        surface = answer['surface']
        
        return hit, surface    
    
    # def filter_json_streams(self, input, output):
    #      sr = JSONStream(input)
    #      while True:
    #          jo = sr.read_next()
    #          if jo is None:
    #              break
    # 
    #          if jo['class'] == 'map':
    #              self.set_map(jo)  
    #          elif jo['class'] == 'sensor':
    #              self.set_sensor(jo)  
    #          elif jo['class'] == 'query':
    #              ### FIXME this is broken
    #              answer = self.query(jo)
    #              simplejson.dump(answer, output)
    #              output.write('\n')
    #          else:
    #              raise Exception, "Uknown format: %s" % jo
 

    
#if __name__ == '__main__':
 #   tr = TexturedRaytracer('raytracer2')
    ### FIXME this is broken (see filter_json_streams )
#    tr.filter_json_streams(sys.stdin, sys.stderr)
    