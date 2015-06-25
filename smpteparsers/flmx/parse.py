from datetime import datetime
from lxml.etree import XMLSyntaxError
from urlparse import urljoin
import logging, requests, json, os

from facility import FacilityParser
from sitelist import SiteListParser
from error import FlmxParseError, FlmxPartialError

# setup logger - __ to ensure it's not accessible from outside
_logger = logging.getLogger(__name__)

class Parser(object):
    """Parser for an FLM-x feed.

    There should be one parser per FLM-x feed, and its sitelist_url should not change.
    """

    def __init__(self, sitelist_url):
        self.sitelist_url = sitelist_url
        self.current_failures = []
        self.is_parsing = False

    def parse(self, username=u'', password=u'', last_ran=datetime.min, failures_file=u'failures.json'):
        """Generator to parse a site list and return the facilities.

        The generator will read the failures from the failures file the first time it is used.
        Then it will yield each facility object in turn when requested, and write any failures
        back at the end.  Using a generator here prevents a large number of subsequent requests
        to the FLM-x endpoint, as processing on the current facility can be done before the next
        is requested.  When the generator is yielded, the parser is considered to be in
        'parsing mode' (the is_parsing flag is set to True).  While in this mode, other methods
        should not change anything which the parser relies on for correct operation.
        Since the failures file is written when the generator exits, any changes
        to the file while the parser is in parsing mode will be overwritten.

        More documentation on the arguments can be found in __init__.py, which provides the public
        interface to this method.
        """
        sp = self.get_sitelist(username=username, password=password)
        sites = sp.get_sites(last_ran)

        all_failures = self.read_failures(failures_file)
        prev_failures = all_failures.get(self.sitelist_url, [])

        # Set parser to 'parsing' mode before wiping current failures
        self.is_parsing = True
        self.current_failures = []

        # Ensure we don't check the failures twice
        for site in set(prev_failures) | set(sites.keys()):
            try:
                fp = self.get_facility(site, username=username, password=password)
            except (requests.exceptions.RequestException, FlmxParseError, FlmxPartialError, XMLSyntaxError) as e:
                _logger.warning(str(e))
                self.current_failures.append(site)
            else:
                _logger.info('returning facility ' + fp.id + ' from ' + self.sitelist_url)
                yield fp

        all_failures[self.sitelist_url] = self.current_failures
        self.write_failures(all_failures, failures_file)
        self.is_parsing = False

    def add_failure(self, site, failures_file=u'failures.json'):
        """Add a failure to the current failures list.

        If the parser is not currently parsing (the parse method is yielded),
        then the failure will be written immediately, otherwise the failure will be written
        by the parse method when it exits.  This is to prevent write conflicts.
        """
        self.current_failures.append(site)

        # If parser is not in parsing mode then write the failure
        # Otherwise it will be written when the parser exits parsing mode
        if not self.is_parsing:
            failures = self.read_failures(failures_file)
            failures[self.sitelist_url] = self.current_failures
            self.write_failures(failures, failures_file)

    def read_failures(self, failures_file):
        """Read the failures file from JSON into a python dict."""
        try:
            with open(os.path.join(os.path.dirname(__file__), failures_file), u'r') as f:
                return json.load(f)
        # IOError if file does not exist, ValueError if file cannot be read or is not valid JSON
        except (IOError, ValueError):
            _logger.warning(failures_file + ' could not be opened, the file will be cleared')
            return {}

    def write_failures(self, failures, failures_file):
        """Write the failures back to the failures file as JSON."""
        with open(os.path.join(os.path.dirname(__file__), failures_file), u'w') as f:
            json.dump(failures, f)

    def request(self, url, username=u'', password=u''):
        res = None
        if username and password:
            res = requests.get(url, auth=(username, password), stream=True)
        else:
            res = requests.get(url, stream=True)

        return res

    def get_sitelist(self, username=u'', password=u''):
        # Get sitelist from URL using authentication if necessary
        res = self.request(self.sitelist_url, username=username, password=password)

        # Raise the HTTPError from requests if there was a problem
        if res.status_code != requests.codes.ok:
            # This reraises a HTTPError stored by the requests API
            _logger.warning('Could not access ' + self.sitelist_url + ': HTTP Response code ' + str(res.status_code))
            res.raise_for_status()

        # response.text auto-converts the response body to a unicode string.
        # This is not compatible with lxml validation so we have to get the raw HTTPResponse,
        # read it, and then wrap it in StringIO so the validator can read it again.
        # If efficiency becomes a problem this is an obvious bottleneck.
        return SiteListParser(res.raw)

    def get_facility(self, url, username=u'', password=u''):
        if u'://' not in url:
            # Assume URL is relative
            url = urljoin(self.sitelist_url, url)

        res = self.request(url, username=username, password=password)

        # If there's a problem with obtaining an FLM
        if res.status_code != 200:
            # This reraises a HTTPError stored by the requests API
            _logger.warning('Could not access ' + url + ': HTTP Response code ' + res.status_code)
            res.raise_for_status()

        try:
            _logger.info('Parsing FLM at ' + url)
            return FacilityParser(res.raw)
        except FlmxParseError as e:
            raise FlmxParseError(u"Problem parsing FLM at " + url + u". Error message: " + e.msg)
        except XMLSyntaxError, e:
            msg = u"FLM at " + url + u" failed validation.  Error message: " + e.msg
            _logger.warning(msg)
            raise XMLSyntaxError(msg)


class ParserMap(object):
    """Controls Parser objects and ensures there is only one parser active per site list."""

    def __init__(self):
        self.parsers = {}

    def get_parser(self, sitelist_url):
        if sitelist_url not in self.parsers:
            self.parsers[sitelist_url] = Parser(sitelist_url)

        return self.parsers[sitelist_url]
