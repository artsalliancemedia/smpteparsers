import parse as flmx
from datetime import datetime
from optparse import OptionParser

def parse(sitelist_url, username=u'', password=u'', last_ran=datetime.min, failures_file=u'failures.json'):
    flmx.parse(sitelist_url, username, password, last_ran, failures_file)

# This main method runs the parser, useful for testing
# but doesn't actually output anything on success 
def main():
    parser = OptionParser(usage=u"%prog [options] url")
    parser.add_option(u"-u", u"--username", dest=u"username", default=u"", help=u"username for authentication")
    parser.add_option(u"-p", u"--password", dest=u"password", default=u"", help=u"password for authentication")
    parser.add_option(u"-f", u"--failures", dest=u"failures", default=u"failures.json", help=u"failures file")

    options, args = parser.parse_args()
    if len(args) != 1:
        print(u"Only one argument is required: the site list URL.")
        exit(1)

    facilities = parse(*args, username=options.username,
                       password=options.password, failures_file=options.failures)

if __name__ == u'__main__':
    main()
