import unittest2

def main():
	loader = unittest2.defaultTestLoader.discover(u'.')
	runner = unittest2.runner.TextTestRunner()
	runner.run(loader)

if __name__ == u'__main__':
	main()
