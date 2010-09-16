from numpy import zeros, eye, dot, array, linalg, deg2rad, arccos, ndarray, rad2deg
from math import atan2, sin, cos
from misc  import  ascolumn
import numpy


def rotz(theta):
    return array([ 
            [ cos(theta), -sin(theta), 0],
            [ sin(theta), cos(theta), 0],
            [0, 0, 1]]) 
    
class RigidBodyState:
    def __init__(self, position=None, attitude=None):
        """ Initialize the object.
        
            Position can be:
            * None (-> [0,0,0] )
            * a list or vector (row or column) with 2 or 3 elements
            
            Attitude can be:
            * None (-> identity)
            * a float (2d orientation, interpreted as angle around z axis)
            * a (3,3) ndarray 
            
            Other values will raise ValueError or TypeError.
        
            After initialization:
                 self.position is a (3,1) vector
                 self.attitude is a (3,3) vector 
        """
        if position == None:
            position = zeros((3, 1))
        if attitude == None:
            attitude = eye(3)
            
        if not (isinstance(position, list) or isinstance(position, ndarray)):
            raise TypeError('Wrong type %s for position' % type(position))
        if not (2 <= len(position) <= 3):
            raise ValueError('Wrong value %s for position' % position)
        if len(position) == 2:
            position = array(position).reshape(2)
            position = array([position[0], position[1], 0]).reshape((3, 1))
        else:
            position = array(position).reshape((3, 1))
        
        # XXX: make this more general
        scalar_types = [float, int, numpy.float32, numpy.float64]
        ok_types = scalar_types + [numpy.ndarray]
        
        if not type(attitude) in ok_types:
            raise TypeError('Wrong type %s for attitude' % type(attitude))
        
        # XXX: make this more general
        if type(attitude) in scalar_types:
            attitude = rotz(float(attitude))
        elif isinstance(attitude, ndarray):
            if len(attitude) == 1:
                attitude = rotz(attitude.flatten()[0])
            elif not attitude.shape == (3, 3):
                raise ValueError('Bad shape for attitude: %s' % str(attitude.shape)) 
        # TODO: check that attitude is indeed a rotation matrix
        
        self.position = position 
        self.attitude = attitude 
        
    def get_2d_position(self):
        """ Get 2-vector corresponding to x,y components """
        p2d = zeros((2, 1))
        p2d[0] = self.position[0, 0]
        p2d[1] = self.position[1, 0]
        return p2d
        
    def get_2d_orientation(self):
        """ Get angle corresponding to orientation """
        forward = array([[1], [0], [0]])
        rotated = dot(self.attitude, forward)
        angle = atan2(rotated[1, 0], rotated[0, 0])
        return float(angle)
    
        
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
            raise TypeError('Expected RigidBodyState, got %s', type(that))
        position = self.position + dot(self.attitude, that.position)
        attitude = dot(self.attitude, that.attitude)
        return RigidBodyState(position=position, attitude=attitude)
    
    def inverse(self):
        """ Returns the inverse transformation """
        attitude = self.attitude.transpose()
        position = -dot(attitude, self.position)
        return RigidBodyState(position=position, attitude=attitude)
    
    def distance(self, other): 
        if not isinstance(other, RigidBodyState):
            raise TypeError('Expected RigidBodyState, got %s', type(other))
        """ Returns a tuple containing the distance in (m, rad) between two configurations """
        T = dot(self.attitude.transpose(), other.attitude).trace() 
        C = (T - 1) / 2
        # make sure that |C| <= 1 (compensate numerical errors), otherwise arccos(1+eps) = nan
        if C > 1: 
            C = 1
        if C < -1:
            C = -1
        distance_rotation = arccos(C)
        distance_translation = linalg.norm(self.position - other.position)
        return (distance_rotation, distance_translation)
    
    def __eq__(self, other):
        distance_rotation, distance_translation = self.distance(other)
        tolerance_rotation = deg2rad(0.0001)
        tolerance_translation = 0.0001
        return (distance_rotation < tolerance_rotation) and (distance_translation < tolerance_translation)
    
    def __str__(self):
        p = self.get_2d_position()
        r = rad2deg(self.get_2d_orientation())
        return '<RigidBody pos=[%+.3fm %+.3fm] rot=%.2fdeg>' % (p[0], p[1], r)
        
