

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
    
    
    