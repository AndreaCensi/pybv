import sys
import simplejson
from jsonstream import JSONStream
from subprocess import Popen, PIPE
# Mainly because we want to use user-defined textures
from numpy import *

class TexturedRaytracer:
    def __init__(self, raytracer='raytracer2'):
        self.p = Popen(raytracer, stdout=PIPE, stdin=PIPE)
        # XXX check errors
        self.child_stream = JSONStream(self.p.stdout)
        self.surface2texture = {}
        
    def set_map(self, map_object):
        for object in map_object['objects']:
            if object.has_key('texture'):
                texture = object.get('texture')
                del object['texture']
            else:
                texture = lambda x: 0.5
            if isinstance(texture, str):
                texture = eval( texture)
            surface = object['surface']
            self.surface2texture[surface] = texture
        
        sys.stderr.write("Textures: %s\n" % self.surface2texture)
#        print map_object
        simplejson.dump(map_object, self.p.stdin)
        self.p.stdin.write('\n') 
        
    def query(self, query_object):
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
                luminance.append( texture(coord)  )
            else:
                luminance.append( float('nan')  )

        answer['luminance'] = luminance
        
        return answer
        
    def set_sensor(self, sensor_object):
        simplejson.dump(sensor_object, self.p.stdin)
        self.p.stdin.write('\n') 
        
        
    def filter_json_streams(self, input, output):
        sr = JSONStream(input)
        while True:
            jo = sr.read_next()
            if jo is None:
                break

            if jo['class'] == 'map':
                self.set_map(jo)  
            elif jo['class'] == 'sensor':
                self.set_sensor(jo)  
            elif jo['class'] == 'query':
                answer = self.query(jo)
                simplejson.dump(answer, output)
                output.write('\n')
            else:
                raise Exception, "Uknown format: %s" % jo


    
if __name__ == '__main__':
    tr = TexturedRaytracer('./raytracer2')
    tr.filter_json_streams(sys.stdin, sys.stderr)
    