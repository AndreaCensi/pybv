import unittest
from pybv.utils import  make_sure_pickable, make_sure_json_encodable
from pybv.worlds import create_random_world

class WorldGenerationTest(unittest.TestCase):
    def testPickling(self):
        """ Make sure that we are generating pickable structures (no lambdas) """
        map = create_random_world(radius=10)
        make_sure_pickable(map)
        make_sure_json_encodable(map)
