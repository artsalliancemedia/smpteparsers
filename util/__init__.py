"""
Utility functions
"""
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from lxml import etree

def get_element(root, tag, namespace):
    """
    Gets the first subelement of root that matches tag. Returns an element
    instance.
    """
    return root.find("{0}{1}{2}{3}".format("{", namespace,"}", tag))

def get_element_text(root, tag, namespace):
    """
    Gets the text in the first subelement of root that matches tag.
    """
    return root.findtext("{0}{1}{2}{3}".format("{", namespace,"}", tag))

def get_element_iterator(root, tag, namespace):
    """
    Creates an iterator which iterates over a list of subelements of root
    that match tag.
    """
    return root.getiterator("{0}{1}{2}{3}".format("{", namespace,"}", tag))

def get_namespace(tag):
    """
    Returns the namespace used in an xml file.
    """
    right_brace = tag.rfind("}")
    return tag[1:right_brace]

def validate_xml(schema_file, xml_file):
    with open(schema_file, 'r') as f:
        schema_root = etree.XML(f.read())

    schema = etree.XMLSchema(schema_root)
    xmlparser = etree.XMLParser(schema=schema)

    try:
        with open(xml_file, 'r') as f:
            etree.fromstring(f.read(), xmlparser)
    except etree.XMLSyntaxError as e:
        # print e
        raise
    except Exception:
        raise
