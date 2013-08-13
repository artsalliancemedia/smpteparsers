from datetime import datetime as dt
from datetime import timedelta
from bs4 import Tag
from StringIO import StringIO
import error, xmlvalidation, os
import logging

_logger = logging.getLogger(__name__)

# These helper methods take XML, strip the tags and
# convert the contents to the required type
def strip_tags(s):
    return s.get_text() if isinstance(s, Tag) else s

def get_boolean(s):
    s = strip_tags(s)
    # Only boolean values in XML are 0 and 1, false and true
    # These string comparisons work as these characters are single byte
    return s != u"0" and s.lower() != u"false" if s else None

def get_string(s):
    # XML contents are already a string so we need to strip the tags
    # and convert to unicode
    return unicode(strip_tags(s)) if s is not None else None

def get_date(s):
    s = strip_tags(s)
    return dt.strptime(s, u"%Y-%m-%d") if s else None

def get_uint(s):
    s = strip_tags(s)
    # No unsigned int in Python
    # int constructor returns a long if it doesn't fit in an int
    return int(s) if s else None

def get_datetime(s):
    u"""Returns the utc datetime for a given ISO8601 date string.

    Format must be as follows: YYYY-mm-ddTHH:MM:SS, with the following optional components
    (that must be in the given order if both are present):

    1. milliseconds eg '.123' (these will be discarded)
    2. timezone given by any of the following:
        * +/-HH:MM
        * +/-HHMM
        * +/-HH

    """
    iso_date = strip_tags(s)
    if not iso_date:
        return None

    date = dt.strptime(iso_date[:19], u"%Y-%m-%dT%H:%M:%S")
    # 19 is up to and including seconds.
    rest = iso_date[19:]

    # rest could be none, any, or all of the following: '.mmm' (millisecs) and '+00:00'
    # Additionally timezone might be in a different format, either +01:00, +0100, or +01
    start_timezone = 0

    # must be millis - 3 extra digits. datetime doesn't store that precision so 
    # we'll just round up so as not to miss this entry when updating
    if rest.startswith(u'.'):
        date += timedelta(seconds = 1)
        # timezone starts after millis
        start_timezone = 4

    hrs = 0
    mins = 0

    timezone = rest[start_timezone:]
    if timezone:
        hrs = int(timezone[:3]) # always should be there
        if len(timezone) > 3:
            mins = int(timezone[-2:])
        # if hrs negative, then mins should be too
        if hrs < 0:
            mins = -mins

    # convert to UTC by subtracting timedelta
    return date - timedelta(hours=hrs, minutes=mins)

# Parses a KDM or DCP delivery list
def deliveries(xml):
    deliveries = {}

    if not xml:
        return deliveries

    if xml.Email:
        deliveries[u'email'] = get_string(xml.EmailAddress)
    if xml.Modem: # Modem, seriously?
        deliveries[u'modem'] = get_string(xml.PhoneNumber)
    if xml.Network:
        deliveries[u'network'] = get_string(xml.URL)
    if xml.Physical:
        deliveries[u'physical'] = get_string(xml.MediaType)

    return deliveries

def validate_XML(xml, xsd):
    u"""Validates an xml object against a given .xsd XML Schema.

    Will raise an `FlmxParseError` if any errors are encountered during the validation process.

    :param string xml: A string object containing the contents of the xml file to validate. 
    :param string xsd: A filename of a .xsd schema file to validate against. 

    """

    v = xmlvalidation.XMLValidator()

    # It is the calling method's responsibility to ensure the pathname works
    # across platforms and OSes
    with open(xsd, u'r') as xsd:
        # If xml is a string, we wrap it in a StringIO object so validate and lxml
        # will work nicely with it
        if isinstance(xml, str) or isinstance(xml, unicode):
            xml = StringIO(xml)
                            
        if not v.validate(xml, xsd):
            error_msg = u""
            # v.get_messages returns a lxml.etree._ListErrorLog object
            for entry in v.get_messages():
                _logger.error('XML Validation failed: ' + repr(entry))
                error_msg += repr(entry) + u"\n"
            raise error.FlmxParseError(error_msg)
