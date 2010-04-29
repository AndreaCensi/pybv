
from pybv.utils import  OpenStruct        

# TODO: make common code?

def random_pose_simulation(
    world_gen, vehicle,
    random_pose_gen, num_iterations,
    processing_class, previous_result=None):
    """
    world
    vehicle
    num_iterations
    random_pose_gen:  XXX lambda -> RigidBodyState
    processing_class
    """
        
    if previous_result is not None:
        state = previous_result
        # if we are called again, it means we need more iteration
        if state.current_iteration == state.total_iterations:   
            state.total_iterations += num_iterations     
    else:
        state = OpenStruct()
        state.current_iteration = 0
        state.total_iterations = num_iterations
        state.result = processing_class(vehicle.config)
        state.vehicle = vehicle

    save_every = 20
    while state.current_iteration < state.total_iterations:
        # sample a random world
        world = world_gen()
        # give the map to the pose generator
        random_pose_gen.set_map(world)
        state1 = random_pose_gen.generate_pose()
        # sets the map for all sensors
        vehicle.set_map(world)
    
        data = vehicle.compute_observations(state1)
        state.result.process_data(data)

        if state.current_iteration % save_every == 0:
            yield state, state.current_iteration, state.total_iterations
        state.current_iteration += 1
        
        

    yield state, state.current_iteration, state.total_iterations


