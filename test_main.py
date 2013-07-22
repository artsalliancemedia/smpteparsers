import unittest2

def main():
    unittest2.runner.TextTestRunner().run(unittest2.defaultTestLoader.discover('.'))

if __name__ == '__main__':
    main()
