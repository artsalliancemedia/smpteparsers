from datetime import datetime as dt
from bs4 import BeautifulSoup
from helper import boolean, string, date, uint, datetime, validate_XML
from operator import attrgetter
from error import FlmxParseError

class FacilityLink(object): 
    """A link to a facility FLM-x file, as contained within a SiteList.

    :var string id_code: The ID of the facility, eg. *"aam.com:UK-ABC-123456-01"*.
    :var datetime last_modified: Last time modified.
    :var string xlink_href: URL of facility FLM-x.
    :var string xlink_type: The type of link, not currently used.  Defaults to *"simple"*.

    """

    id_code = ''
    last_modified = dt.min
    xlink_href = ''
    xlink_type = "simple"

    def __str__(self):
        return 'FacilityLink: \
                id: ' + self.id_code + ', \
                modified: ' + self.last_modified.strftime('%Y-%m-%dT%H:%M:%S') + ' \
                link_href: ' + self.xlink_href + ' \
                link_type: ' + self.xlink_type

class SiteList(object):
    """Contains a list of facilities, and metadata about the site list itself.

    :var string originator: URL of the original FLM file.
    :var string system_name: The name of the system that created this file.
    :var [FacilityLink] facilities: List of ``FacilityLink`` objects.

    """
    originator = ""
    system_name = ""
    facilities = []

class SiteListParser(object):
    """Parses an XML sitelist, and constructs a container holding the the XML document's data.

    :param string xml: Either the contents of an XML file, or a file handle.
        This will parse the contents and construct ``sites``.
    :param boolean validate: Defaults to true. If set, will validate the given
        XML file against the Sitelist XML Schema xsd file, as found on the `FLM-x Homepage`.

    """
    def __init__(self, xml='', validate=True):
        self.contents = xml
        self.sites = SiteList()

        if validate:
            validate_XML(xml, 'schema_sitelist.xsd')

        soup = BeautifulSoup(xml, "xml")

        try:
            self.sites.originator = soup.SiteList.Originator.string
            self.sites.systemName = soup.SiteList.SystemName.string
            facilities = []
            for facility in soup.find_all('Facility'):
                facLink = FacilityLink()
                facLink.id_code = facility['id']
                # strip the timezone from the ISO timecode
                facLink.last_modified = datetime(facility['modified'])
                facLink.xlink_href = facility['xlink:href']
                facLink.xlink_type = facility['xlink:type']

                facilities.append(facLink)
            self.sites.facilities = sorted(facilities, key=attrgetter('last_modified'))
        except Exception, e:
            raise FlmxParseError(repr(e))

    def get_sites(self, last_ran=dt.min):
        """Returns a dictionary mapping URLs as keys to the date that FLM was last modified as a value.

        :param datetime last_ran: a datetime object, with the time given as UTC time, with
            which to search for last_modified times after. defaults to
            ``datetime.min``, that is, to return all FacilityLinks.

        """

        if not last_ran:
            last_ran = dt.min

        return dict((link.xlink_href, link.last_modified)
                    for link in self.sites.facilities
                    if link.last_modified >= last_ran)
