from pybv.utils import RigidBodyState, aslist, OpenStruct
from numpy import cos, sin
from geometry.manifolds import SE2
from geometry.poses import se2_from_linear_angular

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
        
            commands: array of [-1,1] floats 
        """
        inputs = aslist(inputs)
        expected_num_commands = len(self.commands)
        if not (len(inputs) == expected_num_commands):
            raise ValueError, 'I was provided %s' % inputs
        
        actual_commands = {}
        for i, cmd in enumerate(self.commands):
            input = inputs[i]
            assert((input >= -1) and (input <= +1))
            input01 = (input + 1.0) / 2.0
            assert((input01 >= 0) and (input01 <= +1))
            value = cmd.min + input01 * (cmd.max - cmd.min)
            actual_commands[cmd.id] = value
            
        actual_commands = OpenStruct(**actual_commands) 
        return self.integrate(start_state, actual_commands, dt)
        
    def integrate(self, start_state, commands, dt):
        raise Exception, 'Please implement this method'
        
        
        
class OmnidirectionalKinematics(Dynamics):
    def __init__(self, max_linear_velocity=1, max_angular_velocity=1):
        Dynamics.__init__(self)
        
        self.add_command(Command(id='vx', desc='linear velocity (x)',
                                 min= -max_linear_velocity,
                                 max= +max_linear_velocity,
                                 rest=0))
        self.add_command(Command(id='vy', desc='linear velocity (y)',
                                 min= -max_linear_velocity,
                                 max= +max_linear_velocity,
                                 rest=0))
        self.add_command(Command(id='omega', desc='angular velocity',
                                 min= -max_angular_velocity,
                                 max= +max_angular_velocity,
                                 rest=0))
        
    def integrate(self, start, commands, dt):
        velocity = se2_from_linear_angular([commands.vx, commands.vy], commands.omega)
        delta = velocity * dt 
        return SE2.multiply(start, SE2.expmap(SE2.unity(), delta))
    
        
        
        
        
