import os, sys
import pickle
from pybv import BVException
from glob import glob
from os import makedirs
from os.path import expanduser, dirname, join, expandvars, splitext, exists, basename

# TODO: make this configurable

def get_computations_root():
    basepath = '~/svn/cds/pri/bv/src/pybv_experiments_results/computation'
    
    basepath = expandvars(expanduser(basepath))
    
    return basepath

def filename_for_job(job_id):
    """ Returns the pickle storage filename corresponding to the job id """
    #join(dirname(sys.argv[0])
    filename =  join(get_computations_root(), str(job_id) + '.pickle')
    directory = dirname(filename)
    if not exists(directory):
        makedirs(directory)
    return filename

def is_state_available(job_id):
    """ Returns true if there is a previous instance saved """
    filename = filename_for_job(job_id)
    return exists(filename)

def save_state(job_id, state):
    """ Save the state  """
    filename = filename_for_job(job_id)
    dirname = dirname(filename)
    if not exists(dirname):
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
    
    
def list_available_states():
    filename = filename_for_job('*')
    basenames = [ splitext(basename(x))[0] for x in glob(filename)]
    return basenames
    
    
    