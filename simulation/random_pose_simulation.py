import sys, os
from numpy import random, array
from pybv.worlds import  get_safe_pose
from pybv.utils import RigidBodyState, OpenStruct
from pybv.sensors import TexturedRaytracer       
from state_handling import is_state_available, save_state, load_state
from utils import create_progress_bar
from time import time


def random_pose_simulation(
    job_id, world, vehicle, 
    random_pose_gen, num_iterations,
    processing_class):
    """
    job_id
    world
    vehicle
    num_iterations
    random_pose_gen:  lambda iteration -> RigidBodyState
    processing_class
    """
    # sets the map for all sensors
    vehicle.set_map(world)
    
    raytracer = TexturedRaytracer()
    raytracer.set_map(world)
        
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
        state.vehicle = vehicle
        state.world = world

    pbar = create_progress_bar(job_id, state.total_iterations)

    save_every = 20
    while state.current_iteration < state.total_iterations:
        
        if state.current_iteration % save_every == 0:
            state.timestamp = time()
            save_state(job_id, state)
        
        state1 = random_pose_gen(state.current_iteration)
        data = vehicle.compute_observations(state1)
        state.result.process_data(data)

        state.current_iteration += 1
        pbar.update(state.current_iteration)

    state.timestamp = time()
    save_state(job_id, state)
    pbar.update(state.current_iteration)
        
    return state.result

