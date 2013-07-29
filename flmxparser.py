from datetime import datetime
from optparse import OptionParser
from lxml.etree import XMLSyntaxError
import logging, requests, json, os

from flmx.facility import FacilityParser
from flmx.sitelist import SiteListParser
from flmx.error import FlmxParseError, FlmxPartialError

# FLM-x shortcut parser
def parse_flmx(sitelist_url, username=u'', password=u'', last_ran=datetime.min, failures_file=u'failures.json'):
    u"""Parse the FLM site list at the URL provided, and return a list of Facility objects.

    This 'shortcut' parser will get all the facilities referenced by a site list URL and
    present them as a list of Facility objects.  The `last_ran` parameter can be given to
    specify a date to prune the facilities so that only facilities in the site list which
    have been updated since `last_ran` will be returned.  If the URL endpoint requires
    authentication then a `username` and `password` can be given.

    Any failures will be recorded in a JSON file so that the next time the parser runs
    it will retry any failed attempts.  By default this file will be called *failures.json*.
    Be aware that if the `failures_file` provided is corrupt or cannot be parsed as valid JSON
    then it will be overwritten by a valid failures file on the parser's completion,
    and any data in the original file will be lost.

    """
    sp = get_sitelist(sitelist_url, username=username, password=password)
    sites = sp.get_sites(last_ran)

    facilities = []

    with open(os.path.join(os.path.dirname(__file__), failures_file), u'w+') as f:
        try:
            failures = json.load(f)
        # If failures.json is not a valid json file then assume no failures
        except ValueError:
            failures = {}
        prev_failures = failures[sitelist_url] if sitelist_url in failures else []
        new_failures = []

        # Ensure we don't check the failures twice
        for site in set(prev_failures) | set(sites.keys()):
            try:
                fp = get_facility(site, sitelist_url, username=username, password=password)
            except (requests.exceptions.RequestException, FlmxParseError, FlmxPartialError, XMLSyntaxError):
                new_failures.append(site)
            else:
                facilities.append(fp)

        failures[sitelist_url] = new_failures
        json.dump(failures, f)

    return facilities

def request(url, username=u'', password=u''):
    res = None
    if username and password:
        res = requests.get(url, auth=(username, password), stream=True)
    else:
        res = requests.get(url, stream=True)

    return res

def get_sitelist(sitelist_url, username=u'', password=u''):
    # Get sitelist from URL using authentication if necessary
    res = request(sitelist_url, username=username, password=password)

    # Raise the HTTPError from requests if there was a problem
    if res.status_code != 200:
        res.raise_for_status()

    # response.text auto-converts the response body to a unicode string.
    # This is not compatible with lxml validation so we have to get the raw HTTPResponse,
    # read it, and then wrap it in StringIO so the validator can read it again.
    # If efficiency becomes a problem this is an obvious bottleneck.
    return SiteListParser(res.raw.read())

def get_facility(site, sitelist_url, username=u'', password=u''):
    res = request(sitelist_url + site, username=username, password=password)

    # If there's a problem with obtaining an FLM
    if res.status_code != 200:
        # This reraises a HTTPError stored by the requests API
        res.raise_for_status()

    try:
        return FacilityParser(res.raw.read())
    except FlmxParseError, e:
        raise FlmxParseError(u"Problem parsing FLM at " + site + u". Error message: " + e.msg)
    except FlmxPartialError:
        raise
    except XMLSyntaxError, e:
        raise XMLSyntaxError(u"FLM at " + site + u" failed validation.  Error message: " + e.msg)

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

    facilities = parse_flmx(*args, username=options.username,
                            password=options.password, failures_file=options.failures)

if __name__ == u'__main__':
    main()
