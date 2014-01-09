from datetime import datetime as dt
from bs4 import BeautifulSoup
from helper import get_datetime, validate_XML
from operator import attrgetter
from error import FlmxParseError
import os
import logging

_logger = logging.getLogger(__name__)

class FacilityLink(object):
    u"""A link to a facility FLM-x file, as contained within a SiteList.

    :var string id_code: The ID of the facility, eg. *"aam.com:UK-ABC-123456-01"*.
    :var datetime last_modified: Last time modified.
    :var string xlink_href: URL of facility FLM-x.
    :var string xlink_type: The type of link, not currently used.  Defaults to *"simple"*.

    """

    id_code = u''
    last_modified = dt.min
    xlink_href = u''
    xlink_type = u"simple"

    def __str__(self):
        return u'FacilityLink: ' + \
               u'id: ' + self.id_code + u', ' + \
               u'modified: ' + self.last_modified.strftime(u'%Y-%m-%dT%H:%M:%S') + u' ' + \
               u'link_href: ' + self.xlink_href + u' ' + \
               u'link_type: ' + self.xlink_type

class SiteListParser(object):
    u"""A SiteList contains a list of facilities, and metadata about the site list itself.

    :var string originator: URL of the original FLM file.
    :var string system_name: The name of the system that created this file.
    :var [FacilityLink] facilities: A list of ``FacilityLink`` objects.

    """
    originator = u""
    system_name = u""
    facilities = []

    def __init__(self, xml):
        """Parses an XML sitelist, and constructs a container holding the the XML document's data.

        :param string xml: Either the contents of an XML file, or a file handle.
            This will parse the contents and construct ``sites``.
        :param boolean validate: Defaults to true. If set, will validate the given
            XML file against the Sitelist XML Schema xsd file, as found on the `FLM-x Homepage`.

        """

        #If it's a file, we call .read() on it so that it can be consumed twice - once by XMLValidator, and once by
        #beautiful soup
        if not (isinstance(xml, str) or isinstance(xml, unicode)):
            try:
                xml = xml.read()
            except AttributeError as e:
                _logger.critical(repr(e))
                raise FlmxCriticalError(repr(e))

        validate_XML(xml, os.path.join(os.path.dirname(__file__), u'schema', u'schema_sitelist.xsd'))

        soup = BeautifulSoup(xml, u"xml")

        self.originator = soup.SiteList.Originator.string
        self.system_name = soup.SiteList.SystemName.string
        facilities = []
        for facility in soup.find_all(u'Facility'):
            facLink = FacilityLink()
            facLink.id_code = facility[u'id']
            # strip the timezone from the ISO timecode
            facLink.last_modified = get_datetime(facility[u'modified'])
            facLink.xlink_href = facility[u'xlink:href']
            facLink.xlink_type = facility[u'xlink:type']

            facilities.append(facLink)
        self.facilities = sorted(facilities, key=attrgetter(u'last_modified'))

    def get_sites(self, last_ran=dt.min):
        u"""Returns a dictionary mapping URLs as keys to the date that FLM was last modified as a value.

        :param datetime last_ran: a datetime object, with the time given as UTC time, with
            which to search for last_modified times after. defaults to
            ``datetime.min``, that is, to return all FacilityLinks.

        """
        return dict((link.xlink_href, link.last_modified)
                    for link in self.facilities
                    if link.last_modified >= last_ran)
    def __str__(self):
        return str(self.__dict__)
