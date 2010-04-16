import os, sys
import pickle
from pybv import BVException

def filename_for_job(job_id):
    """ Returns the pickle storage filename corresponding to the job id """
    return os.path.join(os.path.dirname(sys.argv[0]), 'computation', str(job_id) + '.pickle')

def is_state_available(job_id):
    """ Returns true if there is a previous instance saved """
    filename = filename_for_job(job_id)
    return os.path.exists(filename)

def save_state(job_id, state):
    """ Save the state  """
    filename = filename_for_job(job_id)
    dirname = os.path.dirname(filename)
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    
    file = open(filename, 'w')
    pickle.dump(state, file, pickle.HIGHEST_PROTOCOL)
    file.close()

def load_state(job_id):
    """ load the state  """
    if not is_state_available(job_id):
        raise BVException('Could not find job %s' % job_id)
    filename = filename_for_job(job_id)
    file = open(filename, 'r')
    state = pickle.load(file)
    file.close()
    return state
    