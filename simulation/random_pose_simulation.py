from numpy import  sqrt  
from pybv.utils import  OpenStruct
from pybv.sensors import TexturedRaytracer       

# TODO: make common code?

def random_pose_simulation(
    world, vehicle,
    random_pose_gen, num_iterations,
    processing_class, previous_result=None):
    """
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
        
    if previous_result is not None:
        state = previous_result
        # if we are called again, it means we need more iteration
        if state.current_iteration == state.total_iterations:
            #ratio = 0.5 * (1 + sqrt(5))
            #state.total_iterations = int(ratio * state.total_iterations)   
            state.total_iterations += num_iterations     
    else:
        state = OpenStruct()
        state.current_iteration = 0
        state.total_iterations = num_iterations
        state.result = processing_class(vehicle.config)
        state.world = world
        state.vehicle = vehicle

    save_every = 20
    while state.current_iteration < state.total_iterations:
        
        if state.current_iteration % save_every == 0:
            yield state, state.current_iteration, state.total_iterations
        
        state1 = random_pose_gen(state.current_iteration)
        data = vehicle.compute_observations(state1)
        state.result.process_data(data)

        state.current_iteration += 1
        

    yield state, state.current_iteration, state.total_iterations


