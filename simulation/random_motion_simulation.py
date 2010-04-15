import sys, os
from numpy import random, array
from pybv.worlds import  get_safe_pose
from pybv.utils import RigidBodyState, OpenStruct
from pybv.sensors import TexturedRaytracer       
from state_handling import is_state_available, save_state, load_state
from utils import create_progress_bar
      
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
    raytracer = TexturedRaytracer()
    raytracer.set_map(world)
        
    # FIXME check whether the computation is the same or parameters changed
    if is_state_available(job_id):
        state = load_state(job_id)
        if state.current_iteration >= state.total_iterations:
            print "%s: using cached results." % job_id
            return state.result
        
    else:
        state = OpenStruct()
        state.current_iteration = 0
        state.total_iterations = num_iterations
        state.result = processing_class(vehicle.config)

    pbar = create_progress_bar(job_id, state.total_iterations)

    save_every = 10
    while state.current_iteration < state.total_iterations:
        
        if state.current_iteration % save_every == 0:
            save_state(job_id, state)
        
        commands = random_commands_gen(state.current_iteration, vehicle)

        state1 = random_pose_gen(state.current_iteration)
        dt = 0.1
        state2 = vehicle.dynamics.evolve_state(state1, commands, dt)
        
        data = vehicle.compute_observations_and_derivatives(state1,state2,dt)
        data.commands =  array(commands)
        
        state.result.process_data(data)

        state.current_iteration += 1
        pbar.update(state.current_iteration)

    pbar.update(state.current_iteration)
    save_state(job_id, state)
    
    return state.result

