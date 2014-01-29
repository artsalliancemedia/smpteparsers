import unittest, os, random
from datetime import datetime
from smpteparsers.cpl import CPL, CPLError

# Cannot use mock objects unfortunately, if we want to use cElementTree we cannot override "__builtin__.open" on that..
base_data_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
cpl_paths = {
    "success": os.path.join(base_data_path, 'success.xml')
}

class TestCPL(unittest.TestCase):
    def test_success(self):
        pass

    def test_id_fails(self):
        pass

if __name__ == '__main__':
    unittest.main()