import unittest2, logging

#logging handler that ignores and discards all messages
class NullHandler(logging.Handler):
    def emit(self, record):
        pass
    def handle(self, record):
        pass    
    def createLock(self):
        pass


def main():
    logger = logging.getLogger()
    logger.addHandler(NullHandler())

    loader = unittest2.defaultTestLoader.discover(u'.')
    runner = unittest2.runner.TextTestRunner()
    runner.run(loader)

if __name__ == u'__main__':
	main()
