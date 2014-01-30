"""
Utility functions
"""
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from lxml import etree

import os, sys

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
    except etree.XMLSyntaxError:
        raise
    except Exception:
        raise

def check_directory(file_path):
    """
    Create the parent directories required for a file if they do not exist.
    os.makedirs() will throw a WindowsError if the folder path already exists
    (which is ok, so we just catch it silently)
    """
    abs_path = os.path.abspath(file_path)
    
    try:
        os.makedirs(abs_path)
    except WindowsError: 
        pass

    return abs_path


def create_link(hard_link_to, source_file):
    """
    Create a hardlink to a file. Should work on both Windows and Unix.
    """
    if sys.platform == 'win32':
        check_directory(os.path.dirname(hard_link_to))

        from ctypes import windll
        from ctypes.wintypes import BOOLEAN, LPWSTR, DWORD, LPVOID
        CreateHardLink = windll.kernel32.CreateHardLinkW
        CreateHardLink.argtypes = (LPWSTR, LPWSTR, LPVOID,)
        CreateHardLink.restype = BOOLEAN
        GetLastError = windll.kernel32.GetLastError
        GetLastError.argtypes = ()
        GetLastError.restype = DWORD

        error_dict = {
                0: 'The operation completed successfully',
                2: 'The system cannot find the file specified',
                3: 'The system cannot find the path specified',
                183: 'Cannot create a file when that file already exists',
                1142: 'An attempt was made to create more links on a file than the file system supports'
        }

        if not CreateHardLink(hard_link_to, source_file, None):
            error_key = GetLastError()
            if error_key in error_dict:
                error = error_dict[error_key]
            else:
                error = 'ErrorKey[%s] not in Error_dict, goto http http://msdn.microsoft.com/en-us/library/ms681382(VS.85).aspx for description '% error_key
            error = error + '|| to: |' + str(hard_link_to) + '| source: |' + str(source_file) + '|'
            raise Exception(error)
    else:
        os.link(source_file, hard_link_to)

def get_file_name(assetmap, dir_path, asset_id, file_ext):
    """
    Get the path for a file by first looking in the INGEST folder for a link
    file. If it is not found, look in the assetmap object. 
    """
    search_path = asset_id + file_ext
    for root, dirs, files in os.walk(dir_path):
        for f in files:
            if f == search_path:
                return os.path.relpath(os.path.join(root, f), dir_path)
    else:
        return assetmap.assets[asset_id].path
