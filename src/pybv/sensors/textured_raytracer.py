import errno
from copy import deepcopy
from StringIO import StringIO
import simplejson #@UnresolvedImport TODO
from subprocess import Popen, PIPE 

from jsonstream import JSONStream #@UnresolvedImport TODO
from pybv.utils import aslist, asscalar, assert_type, assert_has_key
from pybv import BVException

import numpy # used for evaluating functions @UnusedImport
from numpy import array

class TexturedRaytracer:
    def __init__(self, raytracer='raytracer2'):
        self.raytracer = raytracer
        self.p = None
        self.surface2texture = {}
        # This is a copy of the map we received
        self.map = None
        # This is a copy of map, with texture removed, used to send
        # to the C process. The idea is that this is JSON serializable,
        # while map is not
        self.map_purified = None
        self.sensor_desc = None

    def init_connection(self, raytracer):
        try:
            self.p = Popen(raytracer, stdout=PIPE, stdin=PIPE)
            self.child_stream = JSONStream(self.p.stdout)
        #    print "Opened pipe %s, %s" % (self.p.stdin,self.p.stdout) 
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise BVException('Could not open connection to raytracer ("%s"). Reason: %s.' % (raytracer, e.strerror))
            raise e
        
    def write_to_connection(self, object):
        if self.p is None:
            self.init_connection(self.raytracer)
        
        # Make sure that we are sending good json
        sio = StringIO()
        simplejson.dump(object, sio)
        s = sio.getvalue()
        sio2 = StringIO(s)
        simplejson.load(sio2)
        self.p.stdin.write(s)
        self.p.stdin.write('\n') 
        self.p.stdin.flush()
        
    def __del__(self):
        if self.p is not None:
            self.p.stdin.close()
            try:
        #        self.p.terminate()
        #print "Closing pipe %s, %s" % (self.p.stdin,self.p.stdout)
        #       self.p.wait()
                pass
            except OSError:
                pass
        #print " Closed pipe %s, %s" % (self.p.stdin,self.p.stdout)
        
    # pickling
    def __getstate__(self):
        return {'map': self.map,
                'raytracer': self.raytracer,
                'sensor_desc':self.sensor_desc}
    def __setstate__(self, d):
        self.p = None
        self.surface2texture = {}
        self.raytracer = d['raytracer']
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
        self.map_purified = deepcopy(map_object)
        # we also save a copy for calling us again after serialization
        self.map = deepcopy(map_object)

        assert_has_key(self.map_purified, 'objects')
        objects = self.map_purified['objects']
        assert_type(objects, list)
        for object in objects:
            assert_type(object, dict)
            if object.has_key('texture'):
                texture = object.get('texture')
                del object['texture']
            else:
                # FIXME make this configurable
                raise ValueError('texture not provided for object %s. Map was %s' \
                                  % (object, self.map))
#                texture = lambda x: 0.5
            if isinstance(texture, str):
                texture = eval(texture) 
                
            surface = object['surface']
            self.surface2texture[surface] = texture
        
#        sys.stderr.write("Textures: %s\n" % self.surface2texture)
#        print map_object    
    
    def make_sure_raytracer_configured(self):
        if self.map_purified:
            self.write_to_connection(self.map_purified)
        if self.sensor_desc:
            self.write_to_connection(self.sensor_desc)
    
    def query_sensor(self, position, orientation):
        self.make_sure_raytracer_configured()
        
        if self.map is None:
            raise BVException('Sensor queried before map was defined.')
        if self.sensor_desc is None:
            raise BVException('Sensor queried before sensor was defined.')
            
        position = aslist(position)
        orientation = asscalar(orientation)
        query_object = {"class": "query_sensor",
            "position": [position[0], position[1]],
            "orientation": orientation}
        
        self.write_to_connection(query_object)

        answer = self.child_stream.read_next()
        if answer is None:
            raise Exception, "Could not communicate with child"
        
        luminance = []
        for i, surface_id in enumerate(answer['surface']):
            if answer['valid'][i]:
                texture = self.surface2texture[surface_id]
                coord = answer['curvilinear_coordinate'][i]
                luminance.append(asscalar(texture(coord)))
            else:
                luminance.append(float('nan'))
        
        answer['luminance'] = luminance
        
        return answer
        
    def set_sensor(self, sensor_desc):
        self.sensor_desc = sensor_desc
                
    def query_circle(self, center, radius):
        """ Returns tuple (hit, surface_id) """
        if radius is None or center is None:
            raise ValueError('Invalid parameters %s, %s', (center, radius))
        radius = asscalar(radius)
        centera = array(center, dtype='float32')
        if numpy.any(numpy.isnan(centera)) or len(centera) != 2:
            raise ValueError('Invalid parameter center: %s ' % center)
        if not radius > 0:
            raise ValueError('radius must be > 0 (got %s) ' % radius)
        
        center = aslist(center)
        
        self.make_sure_raytracer_configured()

        if self.map is None:
            raise BVException('query_circle called before map was defined.')
        
        query_object = {"class": "query_circle",
            "center": [ center[0], center[1] ],
            "radius": radius}    
         
        self.write_to_connection(query_object)
        answer = self.child_stream.read_next()
        if answer is None:
                raise BVException, "Could not communicate with child"
        assert(answer['class'] == "query_circle_response")
        
        hit = answer['intersects'] == 1
        if hit:
            surface = answer['surface']
        else:
            surface = None
        
        return hit, surface    
    
