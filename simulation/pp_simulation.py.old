from pybv.worlds import  get_safe_pose
from pybv.utils import RigidBodyState
from pybv.sensors import TexturedRaytracer

from pp_dispatcher import Dispatcher
from serial_dispatcher import SerialDispatcher


class RandomPoseSource:
    def __init__(self, num_samples, sensor, radius, safe_zone, num_tries):
        self.num_samples = num_samples
        self.sensor = sensor
        self.radius = radius
        self.safe_zone = safe_zone
        self.num_tries = num_tries
        self.n = 0
        
    def computation_status(self):
        return (self.n, self.num_samples)
        
    def __call__(self):
        if self.n < self.num_samples:
            pose = get_safe_pose(raytracer=self.sensor, world_radius=self.radius, safe_zone=self.safe_zone, num_tries=100)
            self.n += 1
            return (pose, None)
        else:
            return None 

class Observing:
    def __init__(self, vehicle):
        self.init = 0
        self.vehicle = vehicle

    def __call__(self, key, value):
        assert(isinstance(key, RigidBodyState))
        self.vehicle.set_state(key)
        value = self.vehicle.compute_observations()
        return (key, value)

class ReducerWrap:
    def __init__(self, ud):
        self.ud = ud
    def update(self, key, value):
        self.ud.process_data(value)
    def merge(self, that):
        return ReducerWrap( self.ud.merge(that.ud))
        
import sys, os
      
def random_pose_simulator(job_id, world, vehicle, radius, processing_class):
    raytracer = TexturedRaytracer()
    raytracer.set_map(world)
    job_id = os.path.join(os.path.dirname(sys.argv[0]), job_id)
    source = RandomPoseSource(1000, sensor=raytracer, radius=radius, safe_zone=0.5,num_tries=100)
    reducer_class = lambda: ReducerWrap(processing_class(vehicle.config))
    filters = [ Observing(vehicle) ]
    depmods = ('numpy',)
#    depfuncs = ( get_safe_pose, )
    depfuncs = (  )
#    dispatcher = Dispatcher(job_id, source, filters, reducer_class, 4)
# result = dispatcher.run_all(depfuncs=depfuncs, depmods=depmods, batch_size=100)

    dispatcher = SerialDispatcher(job_id, source, filters, reducer_class, 4)
    result = dispatcher.run_all()

    return result.ud


