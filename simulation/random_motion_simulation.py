import sys, os
from numpy import random, array, isnan
from pybv import BVException
from pybv.worlds import  get_safe_pose
from pybv.utils import RigidBodyState, OpenStruct
from pybv.sensors import TexturedRaytracer       
from state_handling import is_state_available, save_state, load_state
from utils import create_progress_bar
from time import time
      
def random_motion_simulation(
    job_id, world, vehicle, 
    random_pose_gen, num_iterations, random_commands_gen, 
    processing_class):
    """
    job_id
    world
    vehicle
    random_pose_gen:  lambda iteration -> RigidBodyState
    random_commands_gen:  lambda iteration, vehicle -> castable to float list
    processing_class
    """
    
    # sets the map for all sensors
    vehicle.set_map(world)
    
    raytracer = TexturedRaytracer()
    raytracer.set_map(world)
        
    # FIXME check whether the computation is the same or parameters changed
    force_recompute = any([x == 'recompute' for x in sys.argv])
    add_iterations = any([x == 'more' for x in sys.argv])
    
    if (not force_recompute) and is_state_available(job_id):
        state = load_state(job_id)
        if (not add_iterations) and (state.current_iteration >= state.total_iterations):
            print "%s: using cached results." % job_id
            return state.result
        
        if add_iterations:
            state.total_iterations += num_iterations
            
    else:
        state = OpenStruct()
        state.job_id = job_id
        state.current_iteration = 0
        state.total_iterations = num_iterations
        state.result = processing_class(vehicle.config)
        state.world = world
        state.vehicle = vehicle

    pbar = create_progress_bar(job_id, state.total_iterations)

    save_every = 10
    while state.current_iteration < state.total_iterations:
        
        if state.current_iteration % save_every == 0:
            state.timestamp = time()
            save_state(job_id, state)
        
        commands = random_commands_gen(state.current_iteration, vehicle)

        state1 = random_pose_gen(state.current_iteration)
        
        if state1 is None:
            raise BVException('Could not generate a random pose.')
            
        dt = 0.1 # TODO make parameter
        state2 = vehicle.dynamics.evolve_state(state1, commands, dt)
        
        data = vehicle.compute_observations_and_derivatives(state1,state2,dt)
        data.commands =  array(commands)
 
        if any(isnan(data.sensels)): 
            raise BVException('Some sensels were NaN. %s' % str(data.sensels))
                
        state.result.process_data(data)

        state.current_iteration += 1
        pbar.update(state.current_iteration)

    pbar.update(state.current_iteration)
    state.timestamp = time()
    save_state(job_id, state)
    
    return state.result

