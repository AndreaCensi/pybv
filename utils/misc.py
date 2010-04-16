from numpy import multiply
import numpy, math
outer = multiply.outer


def weighted_average(A,Aweight,B,Bweight=1):
    """ Computes the weighted average of two quantities A,B. """
    return (A * Aweight + B * Bweight) / (Aweight + Bweight)


from numpy import ndarray, array

def aslist(v):
    """ Flattens an array (whatever shape) to a list. If already list, ignore """
    if isinstance(v, list):
        return v
    elif isinstance(v, ndarray):
        return list(v.flatten())
    else:
        raise TypeError, "aslist() does not support type %s " % type(v)
    
def asscalar(v):
    if isinstance(v, float):
        return v
    elif isinstance(v, int):
        return float(v)
    elif isinstance(v, ndarray):
        if len(v) == 1:
            return float(v[0])
        else:
            raise TypeError, "asscalar() does not support array size %s " % v.shape
    else:
        raise TypeError, "asscalar() does not support type %s " % type(v)
    
    
def ascolumn(v):
    """ Formats the ndarray or list to a column vector (shape (n,1)) """
    v = array(v)
    v = v.flatten()
    n = len(v)
    return v.reshape((n,1))
    
    
    
def cov2corr(M):
    if (not isinstance(M, numpy.ndarray)) or (not (len(M.shape) == 2)) or (not(M.shape[0]==M.shape[1])):
        raise ValueError('cov2corr expects a square ndarray, got %s' % M)

    if numpy.isnan(M).any():
        raise ValueError('Found NaNs in my covariance matrix: %s' % M)

    # TODO check Nan and positive diagonal
    d = M.diagonal()
    if (d < 0).any():
        raise ValueError('Expected positive elements for square matrix, got diag = %s' % d)
    
    n = M.shape[0]
    R = numpy.ndarray((n,n))
    for i in range(n):
        for j in range(n):
            d = M[i,j] / math.sqrt( M[i,i] * M[j,j])
            R[i,j] = d
        
    return R
    
    