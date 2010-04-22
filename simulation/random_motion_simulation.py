import sys, os
from numpy import random, array, isnan
from pybv import BVException
from pybv.worlds import  get_safe_pose
from pybv.utils import RigidBodyState, OpenStruct
from pybv.sensors import TexturedRaytracer       
from time import time
      
def random_motion_simulation(
    world, vehicle, 
    random_pose_gen, num_iterations, random_commands_gen, 
    processing_class, previous_result=None):
    """
    
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
         
    if previous_result is not None:
        state = previous_result
        # if we are called again, it means we need more iteration
        if state.current_iteration == state.total_iterations:
            ratio = 0.5 * (1 + sqrt(5) )
            state.total_iterations *= ratio     
    else:
        state = OpenStruct()
        state.current_iteration = 0
        state.total_iterations = num_iterations
        state.result = processing_class(vehicle.config)
        state.world = world
        state.vehicle = vehicle
        
    save_every = 10
    while state.current_iteration < state.total_iterations:
        
        if state.current_iteration % save_every == 0:
            yield state, state.current_iteration, state.total_iterations
        
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

    yield state, state.current_iteration, state.total_iterations
