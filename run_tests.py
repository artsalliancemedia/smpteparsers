import unittest2

loader = unittest2.defaultTestLoader.discover(u'.')
runner = unittest2.runner.TextTestRunner()
runner.run(loader)
