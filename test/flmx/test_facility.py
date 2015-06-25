# -*- coding: UTF-8 -*-
import unittest, os
from datetime import datetime
from bs4 import BeautifulSoup

from smpteparsers.flmx import facility as flmx
from smpteparsers.flmx import error

class TestFacilityParserMethods(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.path.dirname(__file__), u'testFLM.xml')) as f:
            self.xml = f.read()
            self.fp = flmx.FacilityParser(self.xml)

    def test_get_screens(self):
        screens = self.fp.get_screens()

        # Auditorium object created directly using constructor
        auditorium = flmx.Auditorium(BeautifulSoup(self.xml, u'xml').Auditorium)

        # Check two objects have same values for all fields
        self.assertEqual(screens[1].number, auditorium.number)
        self.assertEqual(screens[1].supports_35mm, auditorium.supports_35mm)
        self.assertEqual(screens[1].name, auditorium.name)
        self.assertEqual(screens[1].screen_aspect_ratio, auditorium.screen_aspect_ratio)
        self.assertEqual(screens[1].adjustable_screen_mask, auditorium.adjustable_screen_mask)
        self.assertEqual(screens[1].audio_format, auditorium.audio_format)
        self.assertEqual(screens[1].install_date, auditorium.install_date)
        self.assertEqual(screens[1].large_format_type, auditorium.large_format_type)

    def test_get_certificates(self):
        certs = self.fp.get_certificates()

        soup = BeautifulSoup(self.xml, u'xml')(u"Auditorium")
        for auditorium in soup:
            screen_index = None
            if auditorium.AuditoriumNumber:
                screen_index = int(auditorium.AuditoriumNumber.get_text())
            elif auditorium.AuditoriumName:
                screen_index = auditorium.AuditoriumName.get_text()
            else:
                self.fail()

            for i, cert_xml in enumerate(auditorium(u"X509Data")):
                # Make certificate object directly from XML snippet
                cert = flmx.Certificate(cert_xml)

                self.assertEqual(certs[screen_index][i].root_name, cert.root_name)
                self.assertEqual(certs[screen_index][i].organization_name, cert.organization_name)
                self.assertEqual(certs[screen_index][i].entity_name, cert.entity_name)
                self.assertEqual(certs[screen_index][i].thumbprint, cert.thumbprint)
                self.assertEqual(certs[screen_index][i].certificate, cert.certificate)


class TestFacilityParser(unittest.TestCase):

    # Minimal validating XML which has FLM partial
    partialXML = """<?xml version="1.0" encoding="UTF-8"?>
        <FacilityListMessage xmlns="http://isdcf.com/2010/06/FLM" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
          <MessageId>urn:uuid:2c87026f-0ec6-4490-8668-bd7647f82e90</MessageId>
          <IssueDate>2013-07-19T09:24:10-10:00</IssueDate>
          <FacilityInfo>
            <FacilityID>urn:x-facilityID:fox.com:5132</FacilityID>
            <FacilityName>A Cinema</FacilityName>
            <Circuit>Independent</Circuit>
            <FLMPartial>1</FLMPartial>
            <AddressList>
              <Address>
                <Physical>
                  <StreetAddress>A Street</StreetAddress>
                  <City>A City</City>
                  <Province>North Island</Province>
                  <Country>UM</Country>
                </Physical>
              </Address>
            </AddressList>
          </FacilityInfo>
          <AuditoriumList>
            <Auditorium>
              <AuditoriumNumber>1</AuditoriumNumber>
              <Supports35MM>false</Supports35MM>
              <DeviceGroupList>
                <DeviceGroup>
                  <Device>
                    <DeviceTypeID>PLY</DeviceTypeID>
                    <DeviceIdentifier idtype="DeviceUID">00000000-0000-0000-0000-000000000000</DeviceIdentifier>
                    <ManufacturerName>Christie</ManufacturerName>
                    <ModelNumber>Solaria One+</ModelNumber>
                    <IsActive>true</IsActive>
                  </Device>
                </DeviceGroup>
              </DeviceGroupList>
            </Auditorium>
          </AuditoriumList>
        </FacilityListMessage>
        """

    emptyXML = """
        """

    unicodeXML = u"""<?xml version="1.0"?>
        <FacilityListMessage xmlns="http://isdcf.com/2010/06/FLM" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
          <MessageId>urn:uuid:2c87026f-0ec6-4490-8668-bd7647f82e90</MessageId>
          <IssueDate>2013-07-19T09:24:10-10:00</IssueDate>
          <FacilityInfo>
            <FacilityID>urn:x-facilityID:fox.com:5132</FacilityID>
            <FacilityName>Cinema</FacilityName>
            <Circuit>Independent</Circuit>
            <AddressList>
              <Address>
                <Physical>
                  <StreetAddress>A Street</StreetAddress>
                  <City>A City</City>
                  <Province>Moscow</Province>
                  <Country>RU</Country>
                </Physical>
              </Address>
            </AddressList>
          </FacilityInfo>
          <AuditoriumList>
            <Auditorium>
              <AuditoriumName>\u2603</AuditoriumName>
              <Supports35MM>false</Supports35MM>
              <DeviceGroupList>
                <DeviceGroup>
                  <Device>
                    <DeviceTypeID>PLY</DeviceTypeID>
                    <DeviceIdentifier idtype="DeviceUID">00000000-0000-0000-0000-000000000000</DeviceIdentifier>
                    <ManufacturerName>Christie</ManufacturerName>
                    <ModelNumber>Solaria One+</ModelNumber>
                    <IsActive>true</IsActive>
                  </Device>
                </DeviceGroup>
              </DeviceGroupList>
            </Auditorium>
          </AuditoriumList>
        </FacilityListMessage>
        """

    def test_partial_FLM(self):
        self.assertRaises(error.FlmxPartialError, flmx.FacilityParser, TestFacilityParser.partialXML)

    def test_empty_FLM(self):
        # This will fail schema validation
        self.assertRaises(error.FlmxParseError, flmx.FacilityParser, TestFacilityParser.emptyXML)

    def test_unicode_FLM(self):
        fp = flmx.FacilityParser(TestFacilityParser.unicodeXML)
        self.assertTrue(u'☃' in fp.auditoriums)


class TestAddress(unittest.TestCase):

    minimalXML = """
        <Address>
          <Shipping>
            <StreetAddress>A Street</StreetAddress>
            <City>A City</City>
            <Province>North Island</Province>
            <Country>UM</Country>
          </Shipping>
        </Address>
        """

    fullXML = """
        <Address>
          <Physical>
            <Addressee>John Smith</Addressee>
            <StreetAddress>A Street</StreetAddress>
            <StreetAddress2>At the corner of another street</StreetAddress2>
            <City>A City</City>
            <Province>North Island</Province>
            <PostalCode>10</PostalCode>
            <Country>UM</Country>
          </Physical>
        </Address>
        """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestAddress.minimalXML, u'xml')
        address = flmx.Address(minimal)

        self.assertEqual(address.street_address, u"A Street")
        self.assertEqual(address.city, u"A City")
        self.assertEqual(address.province, u"North Island")
        self.assertEqual(address.country, u"UM")

        self.assertEqual(address.addressee, None)
        self.assertEqual(address.street_address2, None)
        self.assertEqual(address.postal_code, None)

    def test_optional(self):
        optional = BeautifulSoup(TestAddress.fullXML, u'xml')
        address = flmx.Address(optional)

        self.assertEqual(address.street_address, u"A Street")
        self.assertEqual(address.city, u"A City")
        self.assertEqual(address.province, u"North Island")
        self.assertEqual(address.country, u"UM")

        self.assertEqual(address.addressee, u"John Smith")
        self.assertEqual(address.street_address2, u"At the corner of another street")
        self.assertEqual(address.postal_code, u"10")


class TestContact(unittest.TestCase):

    minimalXML = """
        <Contact>
          <Name>John Smith</Name>
        </Contact>
        """

    fullXML = """
        <Contact>
          <Name>John Smith</Name>
          <CountryCode>UM</CountryCode>
          <Phone1>+56614326431</Phone1>
          <Phone2>0052345322355</Phone2>
          <Email>a@a.com</Email>
          <Type>Manager</Type>
        </Contact>
        """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestContact.minimalXML, u'xml')
        contact = flmx.Contact(minimal)

        self.assertEqual(contact.name, u"John Smith")

        self.assertEqual(contact.country, None)
        self.assertEqual(contact.phone1, None)
        self.assertEqual(contact.phone2, None)
        self.assertEqual(contact.email, None)
        self.assertEqual(contact.type, None)

    def test_optional(self):
        optional = BeautifulSoup(TestContact.fullXML, u'xml')
        contact = flmx.Contact(optional)

        self.assertEqual(contact.name, u"John Smith")

        self.assertEqual(contact.country, u"UM")
        self.assertEqual(contact.phone1, u"+56614326431")
        self.assertEqual(contact.phone2, u"0052345322355")
        self.assertEqual(contact.email, u"a@a.com")
        self.assertEqual(contact.type, u"Manager")


class TestSoftware(unittest.TestCase):

    minimalXML = """
        <Software>
          <Description>A Program</Description>
          <Version>3</Version>
        </Software>
        """

    fullXML = """
        <Software>
          <SoftwareKind>Software</SoftwareKind>
          <SoftwareProducer>AAM</SoftwareProducer>
          <Description>Quantum telecommunication device</Description>
          <Version>0.3b6</Version>
          <FileName>qcomm.exe</Filename>
          <FileSize>1024</FileSize>
          <FileDateTime>3000-01-01T00:00:01-00:00</FileDateTime>
        </Software>
        """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestSoftware.minimalXML, u'xml')
        software = flmx.Software(minimal)

        self.assertEqual(software.description, u"A Program")
        self.assertEqual(software.version, u"3")

        self.assertEqual(software.kind, None)
        self.assertEqual(software.producer, None)
        self.assertEqual(software.filename, None)
        self.assertEqual(software.file_size, None)
        self.assertEqual(software.file_time, None)

    def test_optional(self):
        optional = BeautifulSoup(TestSoftware.fullXML, u'xml')
        software = flmx.Software(optional)

        self.assertEqual(software.description, u"Quantum telecommunication device")
        self.assertEqual(software.version, u"0.3b6")

        self.assertEqual(software.kind, u"Software")
        self.assertEqual(software.producer, u"AAM")
        self.assertEqual(software.filename, u"qcomm.exe")
        self.assertEqual(software.file_size, 1024)
        self.assertEqual(software.file_time, datetime(3000, 1, 1, 0, 0, 1))


class TestIPAddress(unittest.TestCase):

    minimalXML = """
        <IPAddress>
          <Address>1.1.1.1</Address>
        </IPAddress>
        """

    fullXML = """
        <IPAddress>
          <Address>1.1.1.2</Address>
          <Host>host</Host>
        </IPAddress>
        """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestIPAddress.minimalXML, u'xml')
        ip = flmx.IPAddress(minimal)

        self.assertEqual(ip.address, u"1.1.1.1")

        self.assertEqual(ip.host, None)

    def test_optional(self):
        optional = BeautifulSoup(TestIPAddress.fullXML, u'xml')
        ip = flmx.IPAddress(optional)

        self.assertEqual(ip.address, u"1.1.1.2")

        self.assertEqual(ip.host, u"host")


class TestCertificate(unittest.TestCase):

    fullXML = """
        <ds:X509Data>
          <ds:X509SubjectName>CN=fmi.ca.a.com,O=ca.a.com,OU=ca.a.com,dnQualifier=qualifier=</ds:X509SubjectName>
          <ds:X509Certificate>certificate1</ds:X509Certificate>
        </ds:X509Data>
        """

    def test_optional(self):
        optional = BeautifulSoup(TestCertificate.fullXML, u'xml')
        cert = flmx.Certificate(optional)

        self.assertEqual(cert.root_name, u"ca.a.com")
        self.assertEqual(cert.organization_name, u"ca.a.com")
        self.assertEqual(cert.entity_name, u"fmi.ca.a.com")
        self.assertEqual(cert.thumbprint, u"qualifier=")
        self.assertEqual(cert.certificate, u"certificate1")


class TestWatermarking(unittest.TestCase):

    minimalXML = """
        <Watermarking>
          <WatermarkManufacturer>Watermarks Inc.</WatermarkManufacturer>
        </Watermarking>
        """

    fullXML = """
        <Watermarking>
          <WatermarkManufacturer>Watermarks Inc.</WatermarkManufacturer>
          <WatermarkKind>Picture</WatermarkKind>
          <WatermarkModel>Super Watermarker</WatermarkModel>
          <WatermarkVersion>3</WatermarkVersion>
        </Watermarking>
        """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestWatermarking.minimalXML, u'xml')
        watermarking = flmx.Watermarking(minimal)

        self.assertEqual(watermarking.manufacturer, u"Watermarks Inc.")

        self.assertEqual(watermarking.kind, None)
        self.assertEqual(watermarking.model, None)
        self.assertEqual(watermarking.version, None)

    def test_optional(self):
        optional = BeautifulSoup(TestWatermarking.fullXML, u'xml')
        watermarking = flmx.Watermarking(optional)

        self.assertEqual(watermarking.manufacturer, u"Watermarks Inc.")

        self.assertEqual(watermarking.kind, u"Picture")
        self.assertEqual(watermarking.model, u"Super Watermarker")
        self.assertEqual(watermarking.version, u"3")


class TestDevice(unittest.TestCase):

    # This XML has only the mandatory fields defined
    minimalXML = """
        <Device>
          <DeviceTypeID>MDA</DeviceTypeID>
          <DeviceIdentifier idtype="DeviceUID">5a8743a0-f43e-11e2-b778-0800200c9a66</DeviceIdentifier>
          <ManufacturerName>A Company</ManufacturerName>
          <ModelNumber>IMB-3000</ModelNumber>
          <IsActive>false</IsActive>
        </Device>
        """

    # This XML has all the optional fields defined
    fullXML = """
          <Device>
            <DeviceTypeID>PLY</DeviceTypeID>
            <DeviceIdentifier idtype="CertThumbprint">OthN+QPcj6n9v5dhCtTDsnN2v6A=</DeviceIdentifier>
            <DeviceSerial>serial</DeviceSerial>
            <ManufacturerID>urn:x-manufacturerId:fox.com:1560</ManufacturerID>
            <ManufacturerName>Manufacturer</ManufacturerName>
            <ModelNumber>Model</ModelNumber>
            <InstallDate>2013-06-30T16:54:51-10:00</InstallDate>
            <Resolution>2K</Resolution>
            <IsActive>true</IsActive>
            <Integrator>FOX</Integrator>
            <VPFFinanceEntity>FOX</VPFFinanceEntity>
            <VPFStartDate>2013-07-01</VPFStartDate>
            <IPAddressList>""" + TestIPAddress.minimalXML + """</IPAddressList>
            <SoftwareList>""" + TestSoftware.minimalXML + """</SoftwareList>
            <KeyInfoList><ds:KeyInfo>""" + TestCertificate.fullXML + """</ds:KeyInfo></KeyInfoList>
            <WatermarkingList>""" + TestWatermarking.minimalXML + """</WatermarkingList>
            <KDMDeliveryMethodList>
              <DeliveryMethod>
                <Email>
                  <EmailAddress>a@a.com</EmailAddress>
                </Email>
              </DeliveryMethod>
              <DeliveryMethod>
                <Physical>
                  <MediaType>USB</MediaType>
                </Physical>
              </DeliveryMethod>
            </KDMDeliveryMethodList>
            <DCPDeliveryMethodList>
              <DeliveryMethod>
                <Modem>
                  <PhoneNumber>+198074718152987</PhoneNumber>
                </Modem>
              </DeliveryMethod>
            </DCPDeliveryMethodList>
          </Device>
          """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestDevice.minimalXML, u'xml')
        device = flmx.Device(minimal)

        self.assertEqual(device.type, u"MDA")
        self.assertEqual(device.id, u"5a8743a0-f43e-11e2-b778-0800200c9a66")
        self.assertEqual(device.manufacturer_name, u"A Company")
        self.assertEqual(device.model_number, u"IMB-3000")
        self.assertEqual(device.active, False)

        self.assertEqual(device.serial, None)
        self.assertEqual(device.manufacturer_id, None)
        self.assertEqual(device.install_date, None)
        self.assertEqual(device.resolution, None)
        self.assertEqual(device.integrator, None)
        self.assertEqual(device.vpf_finance_entity, None)
        self.assertEqual(device.vpf_start_date, None)
        self.assertEqual(device.ip_addresses, [])
        self.assertEqual(device.software, [])
        self.assertEqual(device.certificates, [])
        self.assertEqual(device.watermarking, [])
        self.assertEqual(device.kdm_deliveries, {})
        self.assertEqual(device.dcp_deliveries, {})

    def test_optional(self):
        optional = BeautifulSoup(TestDevice.fullXML, u'xml')
        device = flmx.Device(optional)

        self.assertEqual(device.type, u"PLY")
        self.assertEqual(device.id, u"OthN+QPcj6n9v5dhCtTDsnN2v6A=")
        self.assertEqual(device.manufacturer_name, u"Manufacturer")
        self.assertEqual(device.model_number, u"Model")
        self.assertEqual(device.active, True)

        self.assertEqual(device.serial, u"serial")
        self.assertEqual(device.manufacturer_id, u"fox.com:1560")
        self.assertEqual(device.install_date, datetime(2013, 7, 1, 2, 54, 51))
        self.assertEqual(device.resolution, u"2K")
        self.assertEqual(device.integrator, u"FOX")
        self.assertEqual(device.vpf_finance_entity, u"FOX")
        self.assertEqual(device.vpf_start_date, datetime(2013, 7, 1))

        self.assertEqual(len(device.ip_addresses), 1)
        self.assertTrue(isinstance(device.ip_addresses[0], flmx.IPAddress))
        self.assertEqual(len(device.software), 1)
        self.assertTrue(isinstance(device.software[0], flmx.Software))
        self.assertEqual(len(device.certificates), 1)
        self.assertTrue(isinstance(device.certificates[0], flmx.Certificate))
        self.assertEqual(len(device.watermarking), 1)
        self.assertTrue(isinstance(device.watermarking[0], flmx.Watermarking))

        self.assertEqual(len(device.kdm_deliveries), 2)
        self.assertTrue(u'email' in device.kdm_deliveries and u'physical' in device.kdm_deliveries)
        self.assertEqual(len(device.dcp_deliveries), 1)
        self.assertTrue(u'modem' in device.dcp_deliveries)


class TestDigital3DSystem(unittest.TestCase):

    minimalXML = """
        <Digital3DSystem>
          <IsActive>0</IsActive>
        </Digital3DSystem>
        """

    fullXML = """
        <Digital3DSystem>
          <IsActive>1</IsActive>
          <Digital3DConfiguration>3D</Digital3DConfiguration>
          <InstallDate>2013-06-30T16:54:51-10:00</InstallDate>
          <ScreenColor>Silver</ScreenColor>
          <ScreenLuminance>23</ScreenLuminance>
          <Ghostbusting>true</Ghostbusting>
          <GhostbustingConfiguration>Good</GhostbustingConfiguration>
        </Digital3DSystem>
        """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestDigital3DSystem.minimalXML, u'xml')
        system = flmx.Digital3DSystem(minimal)

        self.assertEqual(system.active, False)

        self.assertEqual(system.configuration, None)
        self.assertEqual(system.install_date, None)
        self.assertEqual(system.screen_color, None)
        self.assertEqual(system.screen_luminance, None)
        self.assertEqual(system.ghostbusting, None)
        self.assertEqual(system.ghostbusting_configuration, None)

    def test_optional(self):
        optional = BeautifulSoup(TestDigital3DSystem.fullXML, u'xml')
        system = flmx.Digital3DSystem(optional)

        self.assertEqual(system.active, True)

        self.assertEqual(system.configuration, u"3D")
        self.assertEqual(system.install_date, datetime(2013, 7, 1, 2, 54, 51))
        self.assertEqual(system.screen_color, u"Silver")
        self.assertEqual(system.screen_luminance, 23)
        self.assertEqual(system.ghostbusting, True)
        self.assertEqual(system.ghostbusting_configuration, u"Good")


class TestAuditorium(unittest.TestCase):

    minimalXML = """
        <Auditorium>
          <AuditoriumNumber>1</AuditoriumNumber>
          <Supports35MM>false</Supports35MM>
          <DeviceGroupList>
            <DeviceGroup>""" + TestDevice.minimalXML + """</DeviceGroup>
          </DeviceGroupList>
        </Auditorium>
        """

    fullXML = """
        <Auditorium>
          <AuditoriumNumber>2</AuditoriumNumber>
          <AuditoriumName>Screen 2</AuditoriumName>
          <Supports35MM>0</Supports35MM>
          <ScreenAspectRatio>1.85</ScreenAspectRatio>
          <AdjustableScreenMask>Side</AdjustableScreenMask>
          <AudioFormat>13.2</AudioFormat>
          <AuditoriumInstallDate>2013-06-30T16:54:51-10:00</AuditoriumInstallDate>
          <LargeFormatType>Large</LargeFormatType>
          <Digital3DSystem>""" + TestDigital3DSystem.minimalXML + """</Digital3DSystem>
          <DeviceGroupList>
            <DeviceGroup>""" + TestDevice.minimalXML + """</DeviceGroup>
          </DeviceGroupList>
        </Auditorium>
        """

    # This will pass XML schema validation so needs to be tested separately
    noNumberXML = """
        <Auditorium>
          <AuditoriumName>Auditorium</AuditoriumNumber>
          <Supports35MM>false</Supports35MM>
          <DeviceGroupList>
            <DeviceGroup>""" + TestDevice.minimalXML + """</DeviceGroup>
          </DeviceGroupList>
        </Auditorium>
        """

    def test_mandatory(self):
        minimal = BeautifulSoup(TestAuditorium.minimalXML, u'xml')
        auditorium = flmx.Auditorium(minimal)

        self.assertEqual(auditorium.number, 1)
        self.assertEqual(auditorium.supports_35mm, False)
        self.assertEqual(len(auditorium.devices), 1)
        self.assertTrue(isinstance(auditorium.devices[0], flmx.Device))

        self.assertEqual(auditorium.name, None)
        self.assertEqual(auditorium.screen_aspect_ratio, None)
        self.assertEqual(auditorium.adjustable_screen_mask, None)
        self.assertEqual(auditorium.audio_format, None)
        self.assertEqual(auditorium.install_date, None)
        self.assertEqual(auditorium.large_format_type, None)
        self.assertEqual(auditorium.digital_3d_system, None)

    def test_optional(self):
        optional = BeautifulSoup(TestAuditorium.fullXML, u'xml')
        auditorium = flmx.Auditorium(optional)

        self.assertEqual(auditorium.number, 2)
        self.assertEqual(auditorium.supports_35mm, False)
        self.assertEqual(len(auditorium.devices), 1)
        self.assertTrue(isinstance(auditorium.devices[0], flmx.Device))

        self.assertEqual(auditorium.name, u"Screen 2")
        self.assertEqual(auditorium.screen_aspect_ratio, u"1.85")
        self.assertEqual(auditorium.adjustable_screen_mask, u"Side")
        self.assertEqual(auditorium.audio_format, u"13.2")
        self.assertEqual(auditorium.install_date, datetime(2013, 7, 1, 2, 54, 51))
        self.assertEqual(auditorium.large_format_type, u"Large")
        self.assertTrue(isinstance(auditorium.digital_3d_system, flmx.Digital3DSystem))

    def test_no_number(self):
        no_number = BeautifulSoup(TestAuditorium.noNumberXML, u'xml')
        auditorium = flmx.Auditorium(no_number)

        self.assertEqual(auditorium.name, u"Auditorium")
        self.assertEqual(auditorium.supports_35mm, False)
        self.assertEqual(len(auditorium.devices), 1)
        self.assertTrue(isinstance(auditorium.devices[0], flmx.Device))

        self.assertEqual(auditorium.number, None)
        self.assertEqual(auditorium.screen_aspect_ratio, None)
        self.assertEqual(auditorium.adjustable_screen_mask, None)
        self.assertEqual(auditorium.audio_format, None)
        self.assertEqual(auditorium.install_date, None)
        self.assertEqual(auditorium.large_format_type, None)
        self.assertEqual(auditorium.digital_3d_system, None)


class TestFacility(unittest.TestCase):

    # Not a valid FLM but enough to construct a facility
    minimalXML = """<?xml version="1.0" encoding="UTF-8"?>
        <FacilityListMessage xmlns="http://isdcf.com/2010/06/FLM" xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
          <MessageId>urn:uuid:2c87026f-0ec6-4490-8668-bd7647f82e90</MessageId>
          <IssueDate>2013-07-19T09:24:10-10:00</IssueDate>
          <FacilityInfo>
            <FacilityID>urn:x-facilityID:fox.com:5132</FacilityID>
            <FacilityName>A Cinema</FacilityName>
            <Circuit>Independent</Circuit>
            <AddressList>""" + TestAddress.minimalXML + """</AddressList>
          </FacilityInfo>
          <AuditoriumList>""" + TestAuditorium.minimalXML + """</AuditoriumList>
        </FacilityListMessage>

        """

    def test_mandatory(self):
        facility = flmx.FacilityParser(TestFacility.minimalXML)

        self.assertEqual(facility.id, u"fox.com:5132")
        self.assertEqual(facility.name, u"A Cinema")
        self.assertEqual(facility.circuit, u"Independent")

        self.assertTrue(facility.addresses.keys() <= (u'physical', u'shipping', u'billing'))
        for address_type in (u'physical', u'shipping', u'billing'):
            if address_type in facility.addresses:
                self.assertTrue(isinstance(facility.addresses[address_type], flmx.Address))

        # from TestAuditorium.minimalXML
        number = 1
        self.assertEqual(len(facility.auditoriums), 1)
        self.assertTrue(isinstance(facility.auditoriums[number], flmx.Auditorium))

        self.assertEqual(facility.alternate_ids, [])
        self.assertEqual(facility.booking_partner_id, None)
        self.assertEqual(facility.timezone, None)
        self.assertEqual(facility.contacts, [])

    def test_optional(self):
        with open(os.path.join(os.path.dirname(__file__), u'testFLM.xml')) as flm:
            facility = flmx.FacilityParser(flm)

            self.assertEqual(facility.id, u"fox.com:5132")
            self.assertEqual(facility.name, u"A Cinema")
            self.assertEqual(facility.circuit, u"Independent")

            self.assertTrue(facility.addresses.keys() <= (u'physical', u'shipping', u'billing'))
            for address_type in (u'physical', u'shipping', u'billing'):
                if address_type in facility.addresses:
                    self.assertTrue(isinstance(facility.addresses[address_type], flmx.Address))

            # from TestAuditorium.minimalXML
            number = 1
            self.assertEqual(len(facility.auditoriums), 1)
            self.assertTrue(isinstance(facility.auditoriums[number], flmx.Auditorium))

            self.assertEqual(len(facility.alternate_ids), 2)
            self.assertEqual(facility.booking_partner_id, u"fox.com:924")
            self.assertEqual(facility.timezone, u"Pacific/Johnston")
            self.assertEqual(len(facility.contacts), 1)
            self.assertTrue(isinstance(facility.contacts[0], flmx.Contact))
