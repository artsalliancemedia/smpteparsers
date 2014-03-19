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

def validate_xml(schema_file, xml_file, schema_imports=[]):
    with open(schema_file, 'r') as f:
        schema_root = etree.XML(f.read())

    for schema_import in schema_imports:
        new_import = etree.Element('{http://www.w3.org/2001/XMLSchema}import', **schema_import)
        schema_root.insert(0, new_import)

    schema = etree.XMLSchema(schema_root)
    xmlparser = etree.XMLParser(schema=schema)

    with open(xml_file, 'r') as f:
        etree.fromstring(f.read(), xmlparser)

def create_child_element(parent, el_name, el_val):
    """ElementTree Helper method to create a new element with a supplied value
    and attach that element to the specified parent
    :param parent: parent element
    :param el_name: name of the elemnt to create
    :param el_value: text value to be assigned to the element

      e.g.  on the xml, <root />, create_child_element(root, 'foo', 'hello')
      would create:    <root><foo>hello</foo></root>
    """
    el = ET.SubElement(parent, el_name)
    el.text = el_val
    return el

def strip_urn(urn):
    """
    Strips URNs with format urn:<type>:<text> to retrieve the text
    If a valid urn is not supplied, then the original urn is returned
    """
    splitted_urn = urn.split(':')
    if urn.startswith('urn:') and len(splitted_urn) == 3:
        return splitted_urn[2]
    else:
        return urn