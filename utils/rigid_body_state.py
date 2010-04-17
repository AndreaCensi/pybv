from numpy import zeros, eye, dot, array, linalg, deg2rad, arccos
from math import atan2, sin, cos
from misc  import aslist

class RigidBodyState:
    def __init__(self, position = None, attitude = None):
        if position == None:
            position = zeros((3,1))
        if attitude == None:
            attitude = eye(3)
        self.position = position 
        self.attitude = attitude
     #   self.linear_velocity_body = zeros((3,1))
     #   self.angular_velocity_body = zeros((3,1))
        
    def get_2d_position(self):
        """ Get 2-vector corresponding to x,y components """
        p2d = zeros((2,1))
        p2d[0] = self.position[0,0]
        p2d[1] = self.position[1,0]
        return p2d
        
    def get_2d_orientation(self):
        """ Get angle corresponding to orientation """
        forward = array([[1],[0],[0]])
        rotated = dot( self.attitude, forward)
        angle = atan2( rotated[1,0], rotated[0,0])
        return float(angle)
        
    def set_2d_orientation(self, theta):
        self.attitude = array([ 
            [ cos(theta), -sin(theta), 0], 
            [ sin(theta), cos(theta), 0], 
            [0,0,1]] ) 
        
    def set_2d_position(self, position):
        position = aslist(position)
        self.position[0] = position[0]
        self.position[1] = position[1]
        self.position[2] = 0
        
    def oplus(self, that):
        """ Composition of two transformations. 
        
            Args:
                self:  the world->frame1 transformation
                that:  the frame1->frame2 transformation
            Returns:
                the world->frame2 transformation
                
            Example:
            
                vehicle_pose = ...
                sensor_pose = ...
                sensor_pose_world = vehicle_pose.oplus(sensor_pose)
        """
        if not isinstance(that, RigidBodyState):
            raise TypeError('Expected RigidBodyState, got %s', type(that) )
        position = self.position + dot(self.attitude, that.position)
        attitude = dot(self.attitude, that.attitude)
        return RigidBodyState(position=position, attitude=attitude)
    
    def inverse(self):
        """ Returns the inverse transformation """
        attitude = self.attitude.transpose()
        position = - dot(attitude, self.position)
        return RigidBodyState(position=position, attitude=attitude)
    
    def distance(self, other): 
        if not isinstance(other, RigidBodyState):
            raise TypeError('Expected RigidBodyState, got %s', type(other) )
        """ Returns a tuple containing the distance in (m, rad) between two configurations """
        T = dot(self.attitude.transpose(), other.attitude ).trace() 
        C = (T - 1) / 2
        # make sure that |C| <= 1 (compensate numerical errors)
        if C > 1: 
            C = 1
        if C < -1:
            C = -1
        distance_rotation = arccos( C )
        distance_translation = linalg.norm( self.position - other.position )
        return (distance_rotation, distance_translation)
    
    def __eq__(self, other):
        distance_rotation, distance_translation = self.distance(other)
        tolerance_rotation = deg2rad(0.0001)
        tolerance_translation = 0.0001
        return (distance_rotation < tolerance_rotation) and (distance_translation < tolerance_translation)
    
    def __str__(self):
        return '<RigidBody position=%s orientation=%s' % ((aslist(self.get_2d_position())), (self.get_2d_orientation()))
        