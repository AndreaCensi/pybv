from pybv.utils import RigidBodyState, aslist, OpenStruct

class Command:
    def __init__(self, id, desc, min, max, rest):
        self.id = id
        self.desc = desc
        self.min = min
        self.max = max
        self.rest = rest
             
class Dynamics:
    def __init__(self):
        self.commands = []
        
    def add_command(self, command):
        self.commands.append(command)
        
    def evolve_state(self, start_state, inputs, dt):
        """ Returns the evolved state 
        
            commands: array of [0,1] floats 
        """
        assert(isinstance(start_state, RigidBodyState))
        inputs = aslist(inputs)
        expected_num_commands = len(self.commands)
        if not (len(inputs) ==  expected_num_commands):
            raise ValueError, 'I was provided %s' % inputs
            
        actual_commands = {}
        for i, cmd in enumerate(self.commands):
            assert( (inputs[i]>=0) and (inputs[i]<=1) )
            value = cmd.min  + inputs[i] * (cmd.max - cmd.min)
            actual_commands[cmd.id] = value
            
        actual_commands = OpenStruct(**actual_commands) 
        
        return self.integrate(start_state, actual_commands, dt)
        
    def integrate(self, start_state, commands, dt):
        raise Exception, 'Please implement this method'
        
        
    
class OmnidirectionalKinematics(Dynamics):
    def __init__(self, max_linear_velocity=1, max_angular_velocity=1):
        Dynamics.__init__(self)
        
        self.add_command(Command(id='vx',desc='linear velocity (x)', min=-max_linear_velocity, max=+max_linear_velocity, rest=0.5))
        self.add_command(Command(id='vy',desc='linear velocity (y)', min=-max_linear_velocity, max=+max_linear_velocity, rest=0.5))
        self.add_command(Command(id='omega',desc='angular velocity', min=-max_angular_velocity, max=+max_angular_velocity, rest=0.5))
        
    def integrate(self, start_state, commands, dt):
        x = start_state.get_2d_position()[0]
        y = start_state.get_2d_position()[1]
        theta = start_state.get_2d_orientation()
        
        # XXX Simple Euler for now; change later
        x1 = x + commands.vx  * dt
        y1 = y + commands.vy  * dt
        theta1 = theta + commands.omega  * dt
        
        result = RigidBodyState()
        result.set_2d_position([x1,y1])
        result.set_2d_orientation(theta1)
        return result
        
        
        
        
