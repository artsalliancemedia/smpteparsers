from bs4 import BeautifulSoup
from helper import boolean, string, date, uint, datetime, deliveries, validate_XML

class FacilityParser(object):
    """A class to parse a single FLM feed.

    :param xml: an XML string or an open, readable XML file containing an FLM feed.
    :param boolean validate: If true, will validate the XML file against the FLM XML Schema provided by FoxPico.

    Any of the values in the FLM feed can be accessed through the objects given in the next section.
    For example, the screen colour of the 3D system installed in screen #1 can be accessed using
    ``facility.auditoriums[1].digital_3d_system.screen_color``.  Any optional value can be ``None``
    if it is not specified in the FLM.  A value marked *mandatory* is guaranteed to never be ``None``
    providing the original FLM is valid.

    :ivar facility: The top-level facility this FLM feed corresponds to.

    Example usage:

    >>> # Open file handle
    ... with open('flm.xml') as flm:
    ...   # Set up FacilityParser
    ...   fp = flmx.FacilityParser(flm)
    ...   # Get certificates
    ...   certs = fp.get_certificates()
    ...   # Print out the certificates for screen #3 (for example)
    ...   print(certs[3])

    """
    def __init__(self, xml='', validate=True):
        self.contents = xml

        if validate:
            validate_XML(xml, 'schema_facility.xsd')

        flm = BeautifulSoup(self.contents, 'xml')

        if flm.FLMPartial and boolean(flm.FLMPartial):
            pass # Warning for partial FLM?

        self.facility = Facility(flm)

    # Add some more consuming methods, these are just ideas of what data you'd need to get back.
    def get_screens(self):
        """Returns the Auditorium objects corresponding to the screens in the facility.

        This is a dictionary keyed by screen number.

        """
        return self.facility.auditoriums

    def get_certificates(self):
        """Returns all certificates for all of the screens in the facility.

        The certificates are provided in a dictionary keyed by screen number.

        """
        screens = {}

        for key, auditorium in self.facility.auditoriums.iteritems():
            # Flatten certificates for all devices in same auditorium into one list
            certs = [cert for device in auditorium.devices for cert in device.certificates]

            screens[key] = certs

        return screens

class Facility(object):
    """Represents the top-level facility which the FLM refers to.

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
    def __init__(self, flm):
        # Strip the 'urn:x-facilityID' tag from the front of the ID
        self.id = flm.FacilityID.get_text().split(":", 2)[2]
        self.name = string(flm.FacilityName)

        self.alternate_ids = []
        if flm.AlternateFacilityIDList:
            alternate_facilities = flm.AlternateFacilityIDList
            for alternate in alternate_facilities("AlternateFacilityID"):
                self.alternate_ids.append(alternate.get_text().split(":", 2)[2])

        self.booking_partner_id = None
        if flm.BookingPartnerFacilityID:
            self.booking_partner_id = flm.BookingPartnerFacilityID.get_text().split(":", 2)[2]

        self.timezone = string(flm.FacilityTimeZone)
        self.circuit = string(flm.Circuit)

        self.addresses = {}
        address_list = flm.AddressList
        if address_list.Physical:
            self.addresses['physical'] = Address(address_list.Physical)
        elif address_list.Shipping:
            self.addresses['shipping'] = Address(address_list.Shipping)
        elif address_list.Billing:
            self.addresses['billing'] = Address(address_list.Billing)

        self.contacts = []
        if flm.ContactList:
            contact_list = flm.ContactList
            self.contacts = [Contact(contact) for contact in contact_list("Contact")]

        self.auditoriums = {}
        for auditorium in flm("Auditorium"):
            # The auditorium numbers and names are unique for a given facility
            new_auditorium = Auditorium(auditorium)
            if new_auditorium.number:
                self.auditoriums[new_auditorium.number] = new_auditorium
            else:
                self.auditoriums[new_auditorium.name] = new_auditorium


class Address(object):
    """Represents an address.

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
        self.addressee = string(address.Addressee)
        self.street_address = string(address.StreetAddress)
        self.street_address2 = string(address.StreetAddress2)
        self.city = string(address.City)
        self.province = string(address.Province)
        self.postal_code = string(address.PostalCode)
        self.country = string(address.CountryCode)

class Auditorium(object):
    """Represents a screen or auditorium.

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
        self.number = uint(auditorium.AuditoriumNumber)
        self.name = string(auditorium.AuditoriumName)

        self.supports_35mm = boolean(auditorium.Supports35MM)
        self.screen_aspect_ratio = string(auditorium.ScreenAspectRatio) # enum
        self.adjustable_screen_mask = string(auditorium.AdjustableScreenMask) # enum
        self.audio_format = string(auditorium.AudioFormat)
        self.install_date = datetime(auditorium.AuditoriumInstallDate)
        self.large_format_type = string(auditorium.LargeFormatType)

        if auditorium.Digital3DSystem:
            self.digital_3d_system = Digital3DSystem(auditorium.digital_3d_system)

        self.devices = [Device(device) for device in auditorium.DeviceGroupList("Device")]

class Contact(object):
    """Represents a point of contact.

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
        self.name = string(contact.Name)
        self.country = string(contact.CountryCode)
        self.phone1 = string(contact.Phone1)
        self.phone2 = string(contact.Phone2)
        self.email = string(contact.Email)
        self.type = string(contact.Type)

class Device(object):
    """Represents a device in an auditorium.

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
        self.type = string(device.DeviceTypeID)
        self.id = string(device.DeviceIdentifier)
        self.serial = string(device.DeviceSerial)
        self.manufacturer_id = string(device.ManufacturerID)
        self.manufacturer_name = string(device.ManufacturerName)
        self.model_number = string(device.ModelNumber)
        self.install_date = datetime(device.InstallDate.get_text())
        self.resolution = string(device.Resolution)
        self.active = boolean(device.IsActive)

        self.integrator = string(device.Integrator)
        self.vpf_finance_entity = string(device.VPFFinanceEntity)
        self.vpf_start_date = None
        if device.VPFStartDate:
            self.vpf_start_date = date(device.VPFStartDate)

        self.ip_addresses = []
        if device.IPAddressList:
            self.ip_addresses = [IPAddress(ip_address) for ip_address in device.IPAddressList("IPAddress")]

        self.software = []
        if device.SoftwareList:
            self.sotware = [Software(program) for program in device.SoftwareList("Software")]

        self.certificates = []
        if device.KeyInfoList:
            self.certificates = [Certificate(certificate) for certificate in device.KeyInfoList("X509Data")]

        self.watermarking = []
        if device.WatermarkingList:
            self.watermarking = [Watermarking(watermark) for watermark in device.WatermarkingList("Watermarking")]

        self.kdm_deliveries = deliveries(device.KDMDeliveryMethodList)
        self.dcp_deliveries = deliveries(device.DCPDeliveryMethodList)

class Digital3DSystem(object):
    """Represents a digital 3D system installed in an auditorium.

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
        self.active = boolean(system.IsActive)
        self.configuration = string(system.Digital3DConfiguration)
        self.install_date = datetime(system.InstallDate.get_text())
        self.screen_color = string(system.ScreenColor) # enum
        self.screen_luminance = uint(system.ScreenLuminance) # 1 to 29
        self.ghostbusting = boolean(system.ghostbusting)
        self.ghostbusting_configuration = string(system.GhostbustingConfiguration)

class IPAddress(object):
    """Represents an IPv4 or IPv6 address.

    Mandatory fields:

    :ivar string address: The IP address.

    Optional fields:

    :ivar string host: The hostname.

    """
    def __init__(self, ip_address):
        self.address = string(ip_address.Address)
        self.host = string(ip_address.Host)

class Software(object):
    """Represents a version of a device.

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
        self.kind = string(software.SoftwareKind) # enum
        self.producer = string(software.SoftwareProducer)
        self.description = string(software.Description)
        self.version = string(software.Version)
        self.filename = string(software.FileName)
        self.file_size = uint(software.FileSize)
        self.file_time = datetime(software.FileDateTime)

class Certificate(object):
    """Represents an X509 certificate.

    Optional fields:

    :ivar string name: The X509 subject name.
    :ivar string certificate: The X509 certificate.

    """
    def __init__(self, cert):
        self.name = string(cert.X509SubjectName)
        self.certificate = string(cert.X509Certificate)

class Watermarking(object):
    """Represents information about watermarking associated with a device.

    Mandatory fields:

    :ivar string manufacturer: The watermarking manufacturer.
    
    Optional fields:

    :ivar string kind: The type of watermarking.
        Possible values are *picture* or *audio*.
    :ivar string model: The model of the watermarking system.
    :ivar string version: The version of the watermarking system.

    """
    def __init__(self, watermarking):
        self.manufacturer = string(watermarking.WatermarkManufacturer)
        self.kind = string(watermarking.WatermarkKind) # enum
        self.model = string(watermarking.WatermarkModel)
        self.version = string(watermarking.WatermarkModel)
