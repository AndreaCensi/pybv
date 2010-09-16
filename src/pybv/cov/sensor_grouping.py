import numpy
from pybv.utils import weighted_average
from pybv.utils.misc import ascolumn

class SensorGrouping:

    def __init__(self, config):
        n = config.num_sensor
        self.cov_sens = numpy.zeros((n, n))
        self.mean_sens = numpy.zeros((n, 1))
        self.num_samples = 0
        
    def update(self, data):
        y = ascolumn(data.raw_pixels)
        self.mean_sens = weighted_average(self.mean_sens, self.num_samples, y)
        yn = y - self.mean_sens
        yy = numpy.dot(yn, yn.transpose())
        self.cov_sens = weighted_average(self.cov_sens, self.num_samples, yy) 
        self.num_samples += 1
        
    def final_computation(self):
        # do something with covariance
        pass
        
    def parallel_merge(self, that):
        """ Support function for parallel implementation of the simulation """
        self.cov_sens = weighted_average(self.cov_sens, self.num_samples, that.cov_sens, that.num_samples)
        self.mean_sens = weighted_average(self.mean_sens, self.num_samples, that.mean_sens, that.num_samples)        
        self.num_samples += that.num_samples
        
