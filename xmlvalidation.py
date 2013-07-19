from StringIO import StringIO
from lxml import etree

class XMLValidator(object):
    def __init__(self):
        self.messages = []

    def validate(self, xml, xsd, warningsAsErrors=False):
        """Validates a given XML document *xml* against a given schema *xsd*.

        validate uses ``lxml`` to parse and validate the xml. *xml* and *xsd*
        should be passed in as strings. Any errors encountered can be retrieved
        by using the ``get_messages()`` function.

        The *warningsAsErrors* flag can be set to true to make validation fail
        on any warnings.

        Returns a boolean representing validation success.
        """
        if not xml or not xsd:
            return False

        xmlParser = etree.XMLParser()

        schema_doc = etree.parse(xsd)
        schema = etree.XMLSchema(schema_doc)

        xml_doc= etree.parse(xml)
        out = schema.validate(xml_doc)    
        self.messages = schema.error_log
        return out


    def get_messages(self):
        """Returns list of found error messages, stored chronologically. Empty
        if validation has not occurred yet.
        """

        return self.messages

def main():
    validator = XMLValidator()
    xsd = open('sitelist_schema.xsd', 'r')
    xml = StringIO("""<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet href="/2.4.4.19419/static/fort_nocs/xsl/flm/sitelist-to-xhtml.xsl" type="text/xsl"?>
<SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
    <Originator>orig</Originator>
    <SystemName>sysName</SystemName>
    <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
    <FacilityList>
        <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkA" xlink:type="simple"/>
        <Facility id="C" modified="2013-06-09T12:12:03+03:40" xlink:href="linkC" xlink:type="simple"/>
        <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple"/>
    </FacilityList>
</SiteList>""")
    b = validator.validate(xml, xsd)
    print b
    print validator.get_messages()


if __name__ == '__main__':
    main()