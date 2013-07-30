import parse as flmx
from datetime import datetime
from optparse import OptionParser

def parse(sitelist_url, username='', password='', last_ran=datetime.min, failures_file='failures.json'):
    u"""Parse the FLM site list at the URL provided, and return a dict of FacilityParser objects.

    :param string sitelist_url: The URL of the FLM site list.
    :param string username: Username (if required) for authentication at the URL provided.
    :param string password: Password (if required) for authentication.
    :param datetime last_ran: Only FLMs which have been updated since the time specified
        will be returned.  By default all FLMs will be returned.
    :param string failures_file: The path of a JSON file to write the failures to.

    :return: *{string,FacilityParser}* -- The FacilityParser objects are indexed by site id.
        Each object corresponds to a single FLM in the site list.

    This parser will get all the facilities referenced by a site list URL and
    present them as a dict of Facility objects.  The `last_ran` parameter can be given to
    specify a date to prune the facilities so that only facilities in the site list which
    have been updated since `last_ran` will be returned.  If the URL endpoint requires
    authentication then a `username` and `password` can be given.

    Any failures will be recorded in a JSON file so that the next time the parser runs
    it will retry any failed attempts.  By default this file will be called *failures.json*.
    Be aware that if the `failures_file` provided is corrupt or cannot be parsed as valid JSON
    then it will be overwritten by a valid failures file on the parser's completion,
    and any data in the original file will be lost.

    """
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
