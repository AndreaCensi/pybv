from numpy import zeros, eye, dot, array
from math import atan2, sin, cos


class RigidBodyState:
    def __init__(self):
        self.position = zeros((3,1))
        self.attitude = eye(3)
        self.linear_velocity_body = zeros((3,1))
        self.angular_velocity_body = zeros((3,1))
        
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
        position = position.flatten() # XXX generalize?
        self.position[0] = position[0]
        self.position[1] = position[1]
        self.position[2] = 0
        
    def __str__(self):
        return '<RigidBody position=%s orientation=%s' % ((self.get_2d_position()), (self.get_2d_orientation()))
        