import unittest
from StringIO import StringIO

from smpteparsers.flmx import xmlvalidation, error

good_xsd = """<?xml version="1.0" encoding="utf-8"?>
    <schema
        xmlns="http://www.w3.org/2001/XMLSchema"
        targetNamespace="http://isdcf.com/2010/04/SiteList"
        xmlns:tns="http://isdcf.com/2010/04/SiteList"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        elementFormDefault="qualified"
        attributeFormDefault="unqualified">
        <import namespace="http://www.w3.org/1999/xlink" schemaLocation="http://flm.foxpico.com/schema/xlink.xsd"/>
        <import namespace="http://www.w3.org/XML/1998/namespace" schemaLocation="http://flm.foxpico.com/schema/xml.xsd"/>
        <element name="SiteList" type="tns:SiteListType"/>
        <complexType name="SiteListType">
        <sequence>
            <element name="Originator" type="anyURI" />
            <element name="SystemName" type="string" />
            <element name="DateTimeCreated" type="dateTime" />
            <element name="FacilityList" type="tns:FacilityListType">
                <unique name="faclity-id">
                <selector xpath="tns:Facility" />
                <field xpath="@id" />
            </unique>
            </element>
        </sequence>
        </complexType>
        <complexType name="FacilityListType">
        <sequence>
            <element name="Facility" type="tns:FacilityType" maxOccurs="unbounded" minOccurs="0"/>
        </sequence>
        </complexType>
        <complexType name="FacilityType">
        <complexContent>
            <restriction base="anyType">
            <attribute name="id" type="string" use="required" />
            <attribute name="modified" type="dateTime" use="required" />
            <attribute ref="xlink:href" use="required" />
            <attribute ref="xlink:type" use="required" />
            </restriction>
        </complexContent>
        </complexType>
    </schema>
    """

#cuts off halfway
bad_xsd = """<?xml version="1.0" encoding="utf-8"?>
    <schema
        xmlns="http://www.w3.org/2001/XMLSchema"
        targetNamespace="http://isdcf.com/2010/04/SiteList"
        xmlns:tns="http://isdcf.com/2010/04/SiteList"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        elementFormDefault="qualified"
        attributeFormDefault="unqualified">
        <import namespace="http://www.w3.org/1999/xlink" schemaLocation="http://flm.foxpico.com/schema/xlink.xsd"/>
        <import namespace="http://www.w3.org/XML/1998/namespace" schemaLocation="http://flm.foxpico.com/schema/xml.xsd"/>
        <element name="SiteList" type="tns:SiteListType"/>
        <complexType name="SiteListType">
        <sequence>
            <element name="Originator" type="anyURI" />
            <element name="SystemName" type="string" />
            <element name="DateTimeCreated" type="dateTime" />
            <element name="FacilityList" type="tns:FacilityListType">
                <unique name="faclity-id">
                <selector xpath="tns:Facility" />
                <field xpath="@id" />
            </unique>
            </element>
        </sequence>
        </complexType>
        <complexType name="FacilityListType">
        <sequence>
            <element name="Facility" type="tns:FacilityType" maxOccurs="unbounded" minOccurs="0"/>
        </sequence>
        </complexType>
        <complexType name="FacilityType">
        <complexContent>
            <restriction base="anyType">
            <attribute name="id" type="string" use="required" />
            <attribute name="modified" type="dateTime" use="required" />
            <attribute ref="xlink:href" use="required" />"""


good_xml = """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet href="/2.4.4.19419/static/fort_nocs/xsl/flm/sitelist-to-xhtml.xsl" type="text/xsl"?>
    <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
        <Originator>orig</Originator>
        <SystemName>sysName</SystemName>
        <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
        <FacilityList>
            <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkA" xlink:type="simple"/>
            <Facility id="C" modified="2013-06-09T12:12:03+03:40" xlink:href="linkC" xlink:type="simple"/>
            <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple"/>
        </FacilityList>
    </SiteList>"""

#Valid XML, but does not conform to schema - in this case does not have a xlink:href field in Facility
invalid_xml = """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet href="/2.4.4.19419/static/fort_nocs/xsl/flm/sitelist-to-xhtml.xsl" type="text/xsl"?>
    <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
        <Originator>orig</Originator>
        <SystemName>sysName</SystemName>
        <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
        <FacilityList>
            <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:type="simple"/>
            <Facility id="C" modified="2013-06-09T12:12:03+03:40" xlink:type="simple"/>
            <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:type="simple"/>
        </FacilityList>
    </SiteList>"""

#Valid XML, but does not conform to schema - in this case has an extra name field
invalid2_xml = """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet href="/2.4.4.19419/static/fort_nocs/xsl/flm/sitelist-to-xhtml.xsl" type="text/xsl"?>
    <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
        <Originator>orig</Originator>
        <SystemName>sysName</SystemName>
        <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
        <FacilityList>
            <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkA" xlink:type="simple" name="AAA"/>
            <Facility id="C" modified="2013-06-09T12:12:03+03:40" xlink:href="linkC" xlink:type="simple" name="BBB"/>
            <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple" name="CCC"/>
        </FacilityList>
    </SiteList>"""

#Invalid XML
corrupt_xml = """<?xml version="1.0" encoding="UTF-8"?><?xml-stylesheet href="/2.4.4.19419/static/fort_nocs/xsl/flm/sitelist-to-xhtml.xsl" type="text/xsl"?>
    <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
        <Originator>orig</Originator>
        <SystemName>sysName</SystemName>
        <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
        <FacilityList>
            <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkA" xlink:type="simple"/>
            <Facility id="C" modified="2013-06-09T12:12:03+03:40" xlink:href="linkC" xlink:type="simple"/>"""


empty_str = """"""

class TestXMLValidator(unittest.TestCase):
    v = xmlvalidation.XMLValidator()

    def test_goodschema(self):
        # We expect no messages
        self.assertTrue(self.v.validate(StringIO(good_xml), StringIO(good_xsd)))
        self.assertFalse(self.v.get_messages())

        self.assertFalse(self.v.validate(StringIO(invalid2_xml), StringIO(good_xsd)))
        self.assertTrue(self.v.get_messages())

        self.assertFalse(self.v.validate(StringIO(invalid_xml), StringIO(good_xsd)))
        self.assertTrue(self.v.get_messages())

        self.assertFalse(self.v.validate(StringIO(corrupt_xml), StringIO(good_xsd)))
        self.assertTrue(self.v.get_messages())

        self.assertFalse(self.v.validate(StringIO(empty_str), StringIO(good_xsd)))
        self.assertTrue(self.v.get_messages())

    def test_badschema(self):
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(empty_str),    StringIO(bad_xsd))
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(good_xml),     StringIO(bad_xsd))
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(invalid_xml),  StringIO(bad_xsd))
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(corrupt_xml),  StringIO(bad_xsd))

    def test_emptyschema(self):
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(empty_str),    StringIO(empty_str))
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(good_xml),     StringIO(empty_str))
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(invalid_xml),  StringIO(empty_str))
        self.assertRaises(error.FlmxCriticalError, self.v.validate, StringIO(corrupt_xml),  StringIO(empty_str))
