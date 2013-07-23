from datetime import datetime as dt
from datetime import timedelta
from bs4 import BeautifulSoup
from operator import attrgetter
import xmlvalidation

from StringIO import StringIO

def get_datetime(isoDate):
    """returns the utc datetime for a given ISO8601 date string. Format must be
    as follows: YYYY-mm-ddTHH:MM:SS, with the following optional components
    (that must be in the given order if both are present):

    1. milliseconds eg '.123' (these will be discarded)
    2. timezone given by any of the following:
        * +/-HH:MM
        * +/-HHMM
        * +/-HH
    """

    date = dt.strptime(isoDate[:19], "%Y-%m-%dT%H:%M:%S")
    # 19 is up to and including seconds.
    rest = isoDate[19:]


    # rest could be none, any, or all of the following: '.mmm' (millisecs) and '+00:00'
    # Additionally timezone might be in a different format, either +01:00, +0100, or +01
    startTimezone = 0

    #must be millis - 3 extra digits. datetime doesn't store that precision so 
    #we'll just round up so as not to miss this entry when updating
    if rest.startswith('.'):
        date += timedelta(seconds = 1)
        #timezone starts after millis
        startTimezone = 4

    hrs = 0
    mins = 0

    timezone = rest[startTimezone:]
    if timezone:
        hrs = int(timezone[:3]) #always should be there
        if len(timezone) > 3:
            mins = int(timezone[-2:])
        #if hrs negative, then mins should be too
        if hrs < 0:
            mins = -mins

    #convert to UTC by subtracting timedelta
    return date - timedelta(hours=hrs, minutes=mins)

class FlmxParseError(Exception):
    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return self.msg


class FacilityLink(object): 
    """A link to a facility flm file, as contained within a SiteList.
    """
    
     
    id_code = '' 
    """e.g. aam.com:UK-ABC-123456-01
    """
    last_modified = dt.min 
    """Last time modified - defaults to *datetime.min*
    """
    xlink_href = '' 
    """URL of Facility flmx
    """
    xlink_type = "simple"
    """The type of link. Not currently used.
    """

    def __str__(self):
        return 'FacilityLink: \
                id: ' + self.id_code + ', \
                modified: ' + self.last_modified.strftime('%Y-%m-%dT%H:%M:%S') + ' \
                link_href: ' + self.xlink_href + ' \
                link_type: ' + self.xlink_type

class SiteList(object):
    """Contains a list of facilities, and metadata about the site list itself.
    """
    originator = ""
    """URL of the original FLM file
    """
    systemName = ""
    """The name of the system that created this file
    """
    facilities = []
    """List of ``FacilityLink`` objects
    """

def validate_XML(xml, xsd):
    v = xmlvalidation.XMLValidator()
    with open('schema_sitelist.xsd', 'r') as xsd:
        xml_file = xml

        # If xml is a string, we wrap it in a StringIO object so validate and lxml
        # will work nicely with it
        if isinstance(xml, str):
            xml = StringIO(xml)
                            
        if not v.validate(xml, xsd):
            raise FlmxParseError(v.get_messages)

class SiteListParser(object):
    """Parses an xml sitelist, and constructs a container holding the the xml
    document's data.
    """
    def __init__(self, xml='', validate=True, ):
        """``xml`` can either be the contents of an xml file, or a file handle.
        This will parse the contents and construct ``sites``. ``validate`` is an
        optional
        """
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
                # strip  the timezone from the ISO timecode
                facLink.last_modified = get_datetime(facility['modified'])
                facLink.xlink_href = facility['xlink:href']
                facLink.xlink_type = facility['xlink:type']

                facilities.append(facLink)

            self.sites.facilities = sorted(facilities, key=attrgetter('last_modified'))
        except Exception, e:
            raise FlmxParseError(repr(e))


    def get_sites(self, last_ran=dt.min):
        """returns a dictionary mapping URLs as keys to the date that flm was last
        modified as a value.

        *   ``last_ran`` - a datetime object, with the time given as UTC time, with
            which to search for last_modified times after. defaults to
            ``datetime.min``, that is, to return all FacilityLinks.
        """


        if not last_ran:
            last_ran = dt.min

        return dict((link.xlink_href, link.last_modified)
                    for link in self.sites.facilities
                    if link.last_modified >= last_ran)


class FacilityParser(object):
    def __init__(self, xml=''):
        self.contents = xml
        # Do some parsing

    # Add some more consuming methods, these are just ideas of what data you'd need to get back.
    def get_screens():  
        pass

    def get_certificates():
        pass

