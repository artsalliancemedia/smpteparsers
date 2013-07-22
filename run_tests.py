import unittest2

loader = unittest2.defaultTestLoader.discover('.')
runner = unittest2.runner.TextTestRunner()
runner.run(loader)
