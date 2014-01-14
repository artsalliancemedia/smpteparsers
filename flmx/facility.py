from bs4 import BeautifulSoup
from helper import get_boolean, get_string, get_date, get_uint, get_datetime, deliveries, validate_XML
import error, os, logging

_logger = logging.getLogger(__name__)

class FacilityParser(object):
    u"""Represents the top-level facility which the FLM refers to.

    :param xml: an XML string or an open, readable XML file containing an FLM feed.

    Any of the values in the FLM feed can be accessed through the objects given in the next section.
    For example, the screen colour of the 3D system installed in screen #1 can be accessed using
    ``auditoriums[1].digital_3d_system.screen_color``.  Any *optional* value can be ``None``
    if it is not specified in the FLM.  A value marked *mandatory* is guaranteed to never be ``None``
    providing the original FLM is valid.

    Mandatory fields (guaranteed to not be ``None`` for a valid FLM):

    :ivar string id: The facility's unique ID type.
    :ivar string name: The name of the facility.
    :ivar string circuit: The circuit (exhibitor) the facility belongs to.
    :ivar {string,Address} addresses: A dictionary of the addresses for the facility.
        There can be any combination of a *physical*, *shipping* or a *billing* address but there must be at least one.
    :ivar {int/string,Auditorium} auditoriums: The screens in a facility.
        If the auditorium has a number then it is indexed by number.
        Otherwise if it only has a name then it is indexed by name.

    Optional fields (may be ``None`` or empty):

    :ivar [string] alternate_ids: A list of alternate IDs (also unique) for the facility.
    :ivar string booking_partner_id: The ID of the facility's booking partner.
    :ivar string timezone: The time zone name of the facility in TZ format.
    :ivar [string] contacts: A list of people or organisations who are contacts for the facility.

    """

    def __init__(self, xml):

        #If it's a file, we call .read() on it so that it can be consumed twice - once by XMLValidator, and once by
        #beautiful soup
        if not (isinstance(xml, str) or isinstance(xml, unicode)):
            try:
                xml = xml.read()
            except AttributeError as e:
                _logger.critical(repr(e))
                raise error.FlmxCriticalError(repr(e))

        validate_XML(xml, os.path.join(os.path.dirname(__file__), u'schema', u'schema_facility.xsd'))

        flm = BeautifulSoup(xml, u'xml')

        if flm.FLMPartial and get_boolean(flm.FLMPartial):
            msg = u"Partial FLMs not supported"
            _logger.error(msg)
            raise error.FlmxPartialError(u"Partial FLMs are not supported by this parser.")

        self.setup_facility(flm)

    def setup_facility(self, flm):
        # Strip the 'urn:x-facilityID' tag from the front of the ID
        self.id = flm.FacilityID.get_text().split(u":", 2)[2]
        self.name = get_string(flm.FacilityName)

        self.alternate_ids = []
        if flm.AlternateFacilityIDList:
            alternate_facilities = flm.AlternateFacilityIDList
            for alternate in alternate_facilities(u"AlternateFacilityID"):
                self.alternate_ids.append(alternate.get_text().split(u":", 2)[2])

        self.booking_partner_id = None
        if flm.BookingPartnerFacilityID:
            self.booking_partner_id = flm.BookingPartnerFacilityID.get_text().split(u":", 2)[2]

        self.timezone = get_string(flm.FacilityTimeZone)
        self.circuit = get_string(flm.Circuit)

        self.addresses = {}
        address_list = flm.AddressList
        if address_list.Physical:
            self.addresses[u'physical'] = Address(address_list.Physical)
        elif address_list.Shipping:
            self.addresses[u'shipping'] = Address(address_list.Shipping)
        elif address_list.Billing:
            self.addresses[u'billing'] = Address(address_list.Billing)

        self.contacts = []
        if flm.ContactList:
            contact_list = flm.ContactList
            self.contacts = [Contact(contact) for contact in contact_list(u"Contact")]

        self.auditoriums = {}
        for auditorium in flm(u"Auditorium"):
            # The auditorium numbers and names are unique for a given facility
            new_auditorium = Auditorium(auditorium)
            if new_auditorium.number:
                self.auditoriums[new_auditorium.number] = new_auditorium
            else:
                self.auditoriums[new_auditorium.name] = new_auditorium

    # Add some more consuming methods, these are just ideas of what data you'd need to get back.
    def get_screens(self):
        u"""Returns the Auditorium objects corresponding to the screens in the facility.

        This is a dictionary keyed by screen number.

        """
        return self.auditoriums

    def get_certificates(self):
        u"""Returns all certificates for all of the screens in the facility.

        If the screens have numbers, then the certificates are returned in
        a dictionary keyed by screen number.  Otherwise they are keyed by the screen name.

        """
        screens = {}

        for identifier, auditorium in self.auditoriums.iteritems():
            # Flatten certificates for all devices in same auditorium into one list
            certs = [cert for device in auditorium.devices for cert in device.certificates]

            # identifier could be the auditorium name or number
            screens[identifier] = certs

        return screens

    def __repr__(self):
        return str(self.__dict__)

class Address(object):
    u"""Represents an address.

    The addresses of a facility can be *physical*, *shipping* or *billing*.

    Mandatory fields:

    :ivar string street_address: The street line of the address.
    :ivar string city: The city of the address.
    :ivar string province: The province/state/county of the address.
    :ivar string country: The two letter ISO3166 country code where the address resides.

    Optional fields:

    :ivar string addressee: The contact whom the address refers to.
    :ivar string street_address2: The second line of the street in the address.
    :ivar string postal_code: The postal/zip code of the address.

    """
    def __init__(self, address):
        self.addressee = get_string(address.Addressee)
        self.street_address = get_string(address.StreetAddress)
        self.street_address2 = get_string(address.StreetAddress2)
        self.city = get_string(address.City)
        self.province = get_string(address.Province)
        self.postal_code = get_string(address.PostalCode)
        self.country = get_string(address.Country)

    def __repr__(self):
        return str(self.__dict__)

class Auditorium(object):
    u"""Represents a screen or auditorium.

    Mandatory fields:

    :ivar integer number: The number of the auditorium in the facility.
        This is not strictly mandatory as an auditorium may have a name instead of a number,
        but it must have at least one of the two.
    :ivar string supports_35mm: Whether the auditorium supports 35mm film or not.
    :ivar [Device] devices: The devices present in the auditorium.

    Optional fields:

    :ivar string name: The name of the auditorium (eg. *"Auditorium 1"*)
    :ivar string screen_aspect_ratio: The aspect ratio of the screen.
        Possible values are 1.85, 2.39, 1.66, 1.37 or other.
    :ivar string adjustable_screen_mask: The type of the adjustable screen mask.
        Possible values are *top*, *side*, *both* or *none*.
    :ivar string audio_format: The audio format in the auditorium (eg. *"5.1"*).
    :ivar datetime install_date: The install date of the auditorium.
    :ivar string large_format_type: The large format type of the auditorium.
    :ivar Digital3DSystem digital_3d_system: The 3D system installed in the auditorium.

    """
    def __init__(self, auditorium):
        self.number = get_uint(auditorium.AuditoriumNumber)
        self.name = get_string(auditorium.AuditoriumName)

        self.supports_35mm = get_boolean(auditorium.Supports35MM)
        self.screen_aspect_ratio = get_string(auditorium.ScreenAspectRatio) # enum
        self.adjustable_screen_mask = get_string(auditorium.AdjustableScreenMask) # enum
        self.audio_format = get_string(auditorium.AudioFormat)
        self.install_date = get_datetime(auditorium.AuditoriumInstallDate)
        self.large_format_type = get_string(auditorium.LargeFormatType)

        self.digital_3d_system = None
        if auditorium.Digital3DSystem:
            self.digital_3d_system = Digital3DSystem(auditorium.Digital3DSystem)

        self.devices = [Device(device) for device in auditorium.DeviceGroupList(u"Device")]

    def __repr__(self):
        return str(self.__dict__)

class Contact(object):
    u"""Represents a point of contact.

    Mandatory fields:

    :ivar string name: The name of the contact.

    Optional fields:

    :ivar string country: The ISO3166 country code for the contact.
    :ivar string phone1: First phone number for the contact.
    :ivar string phone2: Second phone number for the contact.
    :ivar string email: Email address for the contact.
    :ivar string type: A string categorising the contact.

    """
    def __init__(self, contact):
        self.name = get_string(contact.Name)
        self.country = get_string(contact.CountryCode)
        self.phone1 = get_string(contact.Phone1)
        self.phone2 = get_string(contact.Phone2)
        self.email = get_string(contact.Email)
        self.type = get_string(contact.Type)

    def __repr__(self):
        return str(self.__dict__)

class Device(object):
    u"""Represents a device in an auditorium.

    Mandatory fields:

    :ivar string type: The type of the device defined by SMPTE 433-2008.
        These are given in the table below.
    :ivar string id: A unique ID for the device.  This can be a UUID or a certificate thumbprint.
    :ivar string manufacturer_name: The name of the device manufacturer.
    :ivar string model_number: The model number of the device.
    :ivar boolean active: Whether the device is currently in active use or not.

    Optional fields:

    :ivar string serial: The serial number of the device.
    :ivar string manufacturer_id: A URI corresponding to the ID of the manufacturer.
    :ivar datetime install_date: The device install date.
    :ivar string resolution: The resolution of the device (if a playback device).
        Possible values are *2K*, *4K* and *other*.
    :ivar string integrator: The integrator for the device.
    :ivar string vpf_finance_entity: The entity responsible for VPF on the device.
    :ivar datetime vpf_start_date: The date from which VPF was established on the device.
    :ivar [IPAddress] ip_addresses: Contactable IPv4/IPv6 addresses for the device.
    :ivar [Software] software: A list of installed software on the device.
    :ivar [Certificate] certificates: A list of certificates associated with the device.
    :ivar [Watermarking] watermarking: Watermarks associated with the device.
    :ivar {string,string} kdm_deliveries: A list of methods for delivery of KDMs to the device.
    :ivar {string,string} dcp_deliveries: A list of methods for delivery of DCP content to the device.
        Delivery methods are *email*, *modem*, *network* or *physical*.

    Device Types (SMPTE 433-2008):

    ==== ======================================
    Type Description
    ==== ======================================
    DEC  Media Decoder
    FMI  Forensic Mark Inserter (Image/Picture)
    FMA  Forensic Mark Inserter (Audio/Sound)
    LD   Link Decryptor (Image/Picture)
    LE   Link Encryptor (Image/Picture)
    MDA  Media Decryptor (Audio/Sound)
    MDI  Media Decryptor (Image/Picture)
    MDS  Media Decryptor (Subtitle)
    NET  Networking Device
    PLY  Playback Device
    PR   Projector
    PWR  Power Control System
    SM   Security Manager
    SMS  Screen Management System
    SPB  Secure Processing Block
    TAS  Theater Automation System
    TMS  Theater Management System
    ==== ======================================

    """
    def __init__(self, device):
        self.type = get_string(device.DeviceTypeID)
        self.id = get_string(device.DeviceIdentifier)
        self.serial = get_string(device.DeviceSerial)

        self.manufacturer_id = None
        if device.ManufacturerID:
            self.manufacturer_id = device.ManufacturerID.get_text().split(u":", 2)[2]
        self.manufacturer_name = get_string(device.ManufacturerName)

        self.model_number = get_string(device.ModelNumber)
        self.install_date = get_datetime(device.InstallDate)
        self.resolution = get_string(device.Resolution)
        self.active = get_boolean(device.IsActive)

        self.integrator = get_string(device.Integrator)
        self.vpf_finance_entity = get_string(device.VPFFinanceEntity)
        self.vpf_start_date = None
        if device.VPFStartDate:
            self.vpf_start_date = get_date(device.VPFStartDate)

        self.ip_addresses = []
        if device.IPAddressList:
            self.ip_addresses = [IPAddress(ip_address) for ip_address in device.IPAddressList(u"IPAddress")]

        self.software = []
        if device.SoftwareList:
            self.software = [Software(program) for program in device.SoftwareList(u"Software")]

        self.certificates = []
        if device.KeyInfoList:
            self.certificates = [Certificate(certificate) for certificate in device.KeyInfoList(u"X509Data")]

        self.watermarking = []
        if device.WatermarkingList:
            self.watermarking = [Watermarking(watermark) for watermark in device.WatermarkingList(u"Watermarking")]

        self.kdm_deliveries = deliveries(device.KDMDeliveryMethodList)
        self.dcp_deliveries = deliveries(device.DCPDeliveryMethodList)

    def __repr__(self):
        return str(self.__dict__)

class Digital3DSystem(object):
    u"""Represents a digital 3D system installed in an auditorium.

    Mandatory fields:

    :ivar boolean active: Whether the 3D system is active or not.

    Optional fields:

    :ivar string configuration: A string describing the 3D configuration, eg. *"RealD"* or *"Dolby 3D"*.
    :ivar datetime install_date: The install date of the 3D system.
    :ivar string screen_color: The colour of the screen.
        Possible values are *silver*, *white* or *other*.
    :ivar integer screen_luminance: The luminance of the screen.
        Possible values are between 1 and 29 (inclusive).
    :ivar boolean ghostbusting: Whether the screen supports ghostbusting technology.
    :ivar string ghostbusting_configuration: Details of the ghostbusting configuration.

    """
    def __init__(self, system):
        self.active = get_boolean(system.IsActive)
        self.configuration = get_string(system.Digital3DConfiguration)
        self.install_date = get_datetime(system.InstallDate)
        self.screen_color = get_string(system.ScreenColor) # enum
        self.screen_luminance = get_uint(system.ScreenLuminance) # 1 to 29
        self.ghostbusting = get_boolean(system.Ghostbusting)
        self.ghostbusting_configuration = get_string(system.GhostbustingConfiguration)

    def __repr__(self):
        return str(self.__dict__)

class IPAddress(object):
    u"""Represents an IPv4 or IPv6 address.

    Mandatory fields:

    :ivar string address: The IP address.

    Optional fields:

    :ivar string host: The hostname.

    """
    def __init__(self, ip_address):
        self.address = get_string(ip_address.Address)
        self.host = get_string(ip_address.Host)

    def __repr__(self):
        return str(self.__dict__)

class Software(object):
    u"""Represents a version of a device.

    This can be used to describe any versionable portion of a device, and not just software.

    Mandatory fields:

    :ivar string description: A description of the software (such as the name).
    :ivar string version: The software version.

    Optional fields:

    :ivar string kind: The type of the software.
        Possible values are *firmware*, *software* or *hardware*.
    :ivar string producer: The software producer.
    :ivar string filename: The name of the file.
    :ivar integer file_size: Size of the file.
    :ivar datetime file_time: A time associated with the file, for versioning purposes.

    """
    def __init__(self, software):
        self.kind = get_string(software.SoftwareKind) # enum
        self.producer = get_string(software.SoftwareProducer)
        self.description = get_string(software.Description)
        self.version = get_string(software.Version)
        self.filename = get_string(software.FileName)
        self.file_size = get_uint(software.FileSize)
        self.file_time = get_datetime(software.FileDateTime)

    def __repr__(self):
        return str(self.__dict__)

class Certificate(object):
    u"""Represents an X.509 certificate.

    The certificate format is defined by IETF PKIX_, with the fields used
    in accordance with SMPTE 430-2-2006.  The latter document describes specific
    constraints to the X.509 standard for use in digital cinema.  Specifically
    there is a mapping of digital cinema identity attributes to commonly used
    X.509 name attributes, which is handled by this parser.

    Optional fields:

    :ivar string subject_name: The entire X.509 subject name field.  This contains the root name,
        organization name, entity name and thumbprint.
    :ivar string root_name: Name of the organization holding the root of the certificate
        chain.  This is parsed from the X.509 *OrganizationName* attribute.
    :ivar string organization_name: Name of the organization to which the issuer or subject of
        the certificate belongs.  This usually refers to the device maker.  It is parsed
        from the X.509 *OrganizationUnitName* attribute.
    :ivar string entity_name: Entity issuing the certificate or being issued the certificate.
        This is parsed from the X.509 *CommonName* attribute.
    :ivar string thumbprint: The unique thumbprint of the public key of the entity
        issuing the certificate or being issued the certificate; also known as *dnQualifier*.
    :ivar string certificate: The X.509 certificate.

    .. _PKIX: http://www.ietf.org/rfc/rfc5280.txt

    """
    def __init__(self, cert):
        self.subject_name = get_string(cert.X509SubjectName)

        fields = {}
        if self.subject_name is not None:
            for attribute in self.subject_name.split(u','):
                # kv_pair is, for example, "OU=DLP-Cinema.TexasInstruments"
                # We split it on the first equals (incase the val contains an equals)
                # If there are 2 items, we store the pair in the fields dict
                kv_pair = attribute.strip().split(u'=', 1)
                if len(kv_pair) == 2:
                    fields[kv_pair[0].lower()] = kv_pair[1]

        # dict.get returns None if key not in dict
        self.root_name = fields.get(u'o')
        self.organization_name = fields.get(u'ou')
        self.entity_name = fields.get(u'cn')
        self.thumbprint = fields.get(u'dnqualifier') or fields.get(u'dnq')

        self.certificate = get_string(cert.X509Certificate)

    def __repr__(self):
        return str(self.__dict__)

class Watermarking(object):
    u"""Represents information about watermarking associated with a device.

    Mandatory fields:

    :ivar string manufacturer: The watermarking manufacturer.

    Optional fields:

    :ivar string kind: The type of watermarking.
        Possible values are *picture* or *audio*.
    :ivar string model: The model of the watermarking system.
    :ivar string version: The version of the watermarking system.

    """
    def __init__(self, watermarking):
        self.manufacturer = get_string(watermarking.WatermarkManufacturer)
        self.kind = get_string(watermarking.WatermarkKind) # enum
        self.model = get_string(watermarking.WatermarkModel)
        self.version = get_string(watermarking.WatermarkVersion)

    def __repr__(self):
        return str(self.__dict__)
