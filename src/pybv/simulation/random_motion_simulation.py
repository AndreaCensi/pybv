from numpy import  array
from pybv import BVException
from pybv.utils import  OpenStruct
import numpy
from pybv.utils.numpy_utils import  assert_reasonable_value
      
def random_motion_simulation(
    world_gen, vehicle,
    random_pose_gen, num_iterations, random_commands_gen, dt,
    processing_class, previous_result=None):
    """
    
    world
    vehicle
    random_pose_gen:  lambda iteration -> RigidBodyState
    random_commands_gen:  lambda iteration, vehicle -> castable to float list
    processing_class
    """
    
    # Use random seed
    numpy.random.seed()
         
    if previous_result is not None:
        state = previous_result
        # if we are called again, it means we need more iteration
        if state.current_iteration == state.total_iterations:
            state.total_iterations += num_iterations
            print "Increasing to %d iterations" % state.total_iterations
    else:
        state = OpenStruct()
        state.current_iteration = 0
        state.total_iterations = num_iterations
        state.result = processing_class(vehicle.config)
        state.vehicle = vehicle
        
    save_every = 50
    generate_world_every = 5
    world = None
    while state.current_iteration < state.total_iterations:
        # sample a random world
        if world is None or  \
            state.current_iteration % generate_world_every == 0:
            world = world_gen()
            # give the map to the pose generator
            random_pose_gen.set_map(world)
            # sets the map for all sensors
            vehicle.set_map(world)
    
        state1 = random_pose_gen.generate_pose()
        if state1 is None:
            raise BVException('Could not generate a random pose.')

        # generate random commands
        commands = random_commands_gen(state.current_iteration, vehicle)
        # get next state
        state2 = vehicle.dynamics.evolve_state(state1, commands, dt)
        
        data = vehicle.compute_observations_and_derivatives(state1, state2, dt)
        data.commands = array(commands)
 
 
        assert_reasonable_value(data.sensels)
        assert_reasonable_value(data.sensels_dot)
        
        #
#        for i, v in enumerate(data.sensels):
#            if v < 0.5:
#                print "Found sensel %d: range %f surf %s valid %s" % \
#                    (i, v, data.rangefinder[0].surface[i], \
#                      data.rangefinder[0].valid[i], \
#                     ) # data.surface[i])
#                #print data.rangefinder[0].__dict__.keys() 
#                print world
#                break
#                    
        state.result.process_data(data)
        
        # housekeeping
        if state.current_iteration % save_every == 0:
            yield state, state.current_iteration, state.total_iterations
        state.current_iteration += 1

    yield state, state.current_iteration, state.total_iterations
