from StringIO import StringIO
from lxml import etree
from lxml.etree import XMLSyntaxError   
import flmx

class XMLValidator(object):
    def __init__(self):
        self.messages = []

    def validate(self, xml, xsd):
        """Validates a given XML document *xml* against a given schema *xsd*.

        validate uses ``lxml`` to parse and validate the xml. *xml* and *xsd*
        should be passed in as strings. Any errors encountered can be retrieved
        by using the ``get_messages()`` function.

        Returns a boolean representing validation success.
        """
        if not xml or not xsd:
            return False

        schema_doc = None
        xml_doc = None

        try:
            schema_doc = etree.parse(xsd)
        except XMLSyntaxError, e:
            raise flmx.FlmxParseError("Schema could not be parsed: " + repr(e))
        # Decided not to wrap IOError here - it should be a different issue if file can't be opened!
        # except IOError, e:
        #     raise flmx.FlmxParseError("Schema could not be opened: " + repr(e))

        #Not mission critical if the xml file does not parse - just return false as does not validate. 
        try:
            xml_doc= etree.parse(xml)
        except XMLSyntaxError, e:
            self.messages = ["XML document could not be parsed: " + repr(e)]
            return False
        # except IOError, e:
        #     raise flmx.FlmxParseError("XML document could not be opened: " + repr(e))

        schema = etree.XMLSchema(schema_doc)
        out = schema.validate(xml_doc)    
        self.messages = schema.error_log
        return out


    def get_messages(self):
        """Returns list of found error messages, stored sequentially. An empty list 
        if validation has not occurred yet, or if there were no error messages
        """

        return self.messages
