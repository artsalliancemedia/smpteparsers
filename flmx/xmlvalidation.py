from lxml import etree
from lxml.etree import XMLSyntaxError
from error import FlmxCriticalError, FlmxParseError
import logging

_logger = logging.getLogger(__name__)


class XMLValidator(object):
    u"""Tool to validate XML documents against schemas using lxml.

    Example usage:

    >>> # Open files
    ... with open(u'example.xsd') as xsd:
    ...   with open(u'example.xml') as xml:
    ...     validator = XMLValidator()
    ...     if not validator.validate(xml, xsd):
    ...         print validator.get_messages()

    """


    def __init__(self):
        self.messages = []

    def validate(self, xml, xsd):
        u"""Validates a given XML document *xml* against a given schema *xsd*.

        :param file xml: An open file-like object containing the xml file.
        :param file xsd: An open file-like object containing the xsd schema to validate against.

        validate uses ``lxml`` to parse and validate the xml. *xml* and *xsd*
        should be passed in as strings. Any errors encountered can be retrieved
        by using the ``get_messages()`` function.

        :return: *boolean* -- Validation success. If false, `get_messages` will contain any provided error messages.
        """
        if not xml or not xsd:
            msg = u'Must provide both xml and xsd files.'
            _logger.critical(msg)
            raise FlmxCriticalError(msg)

        schema_doc = None
        xml_doc = None

        try:
            schema_doc = etree.parse(xsd)
        except XMLSyntaxError, e:
            msg= u"Schema could not be parsed: " + repr(e)
            _logger.critical(msg)
            raise FlmxCriticalError(msg)

        # Not mission critical if the xml file does not parse - just return false as does not validate.
        try:
            xml_doc = etree.parse(xml)
        except XMLSyntaxError, e:
            msg = u"XML document could not be parsed: " + repr(e)
            self.messages = [msg]
            _logger.warning(msg)
            return False

        schema = etree.XMLSchema(schema_doc)
        out = schema.validate(xml_doc)
        self.messages = schema.error_log
        return out


    def get_messages(self):
        u"""
        :return: *list(string)* -- A list of found error messages, stored sequentially. Will be an empty list if there were no error messages.
        """

        return self.messages
