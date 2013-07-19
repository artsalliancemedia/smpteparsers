from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from operator import attrgetter

# These helper methods take XML, strip the tags and
# convert the contents to the required type
def boolean(s):
    if not s:
        return None

	string = s.get_text()
	# Only boolean values in XML are 0 and 1, false and true
	return string != "0" and string.lower() != "false"

def string(s):
    return None if not s else s.get_text()

def date(s):
    if not s:
        return None

	string = s.get_text
	return datetime.strptime(string, "%Y-%m-%d")

def uint(s):
    if not s:
        return None

    string = s.get_text()
    # No unsigned int in Python
    # int constructor returns a long if it doesn't fit in an int
    return int(string)

# Parses a KDM or DCP delivery list
def deliveries(xml):
    deliveries = {}

    if not xml:
        return deliveries

    if xml.Email:
        deliveries['email'] = xml.EmailAddress.get_text()
    if xml.Modem: # Modem, seriously?
        deliveries['modem'] = xml.PhoneNumber.get_text()
    if xml.Network:
        deliveries['network'] = xml.URL.get_text()
    if xml.Physical:
        deliveries['physical'] = xml.MediaType.get_text()

    return deliveries

def get_datetime(isoDate):
    """returns the utc datetime for a given ISO8601 date string. Format must be
    as follows: YYYY-mm-ddTHH:MM:SS, with the following optional components
    (that must be in the given order if both are present):

    1. milliseconds eg '.123' (these will be discarded)
    2. timezone given by any of the following:
        * +/-HH:MM
        * +/-HHMM
        * +/-HH
    """

    dt = datetime.strptime(isoDate[:19], "%Y-%m-%dT%H:%M:%S")
    # 19 is up to and including seconds.
    rest = isoDate[19:]


    # rest could be none, any, or all of the following: '.mmm' (millisecs) and '+00:00'
    # Additionally timezone might be in a different format, either +01:00, +0100, or +01
    startTimezone = 0

    #must be millis - 3 extra digits. datetime doesn't store that precision so 
    #we'll just round up so as not to miss this entry when updating
    if rest.startswith('.'):
        dt += timedelta(seconds = 1)
        #timezone starts after millis
        startTimezone = 4

    hrs = 0
    mins = 0

    timezone = rest[startTimezone:]
    if timezone:
        hrs = int(timezone[:3]) #always should be there
        if len(timezone) > 3:
            mins = int(timezone[-2:])
        #if hrs negative, then mins should be too
        if hrs < 0:
            mins = -mins

    #convert to UTC by subtracting timedelta
    return dt - timedelta(hours=hrs, minutes=mins)

class FacilityLink(object): 
    """A link to a facility flm file, as contained within a SiteList.
    """
    
     
    id_code = '' 
    """e.g. aam.com:UK-ABC-123456-01
    """
    last_modified = datetime.min 
    """Last time modified
    """
    xlink_href = '' 
    """URL of Facility flmx
    """
    xlink_type = "simple"
    """The type of link. Not currently used.
    """

    def __str__(self):
        return 'FacilityLink: \
                id: ' + self.id_code + ', \
                modified: ' + self.last_modified.strftime('%Y-%m-%dT%H:%M:%S') + ' \
                link_href: ' + self.xlink_href + ' \
                link_type: ' + self.xlink_type



class SiteList(object):
    """Contains a list of facilities, and metadata about the site list itself.
    """
    originator = ""
    """URL of the original FLM file
    """
    systemName = ""
    """The name of the system that created this file
    """
    facilities = []
    """List of ``FacilityLink`` objects
    """

class SiteListParser(object):
    """Parses an xml sitelist, and constructs a container holding the the xml
    document's data.
    """
    def __init__(self, xml='', validate=True, ):
        """``xml`` can either be the contents of an xml file, or a file handle.
        This will parse the contents and construct ``sites``. ``validate`` is an
        optional
        """
        self.contents = xml
        self.sites = SiteList()

        soup = BeautifulSoup(xml, "xml")
        self.sites.originator = soup.SiteList.Originator.string
        self.sites.systemName = soup.SiteList.SystemName.string
        facilities = []
        for facility in soup.find_all('Facility'):
            facLink = FacilityLink()
            facLink.id_code = facility['id']
            # strip  the timezone from the ISO timecode
            facLink.last_modified = get_datetime(facility['modified'])
            facLink.xlink_href = facility['xlink:href']
            facLink.xlink_type = facility['xlink:type']

            facilities.append(facLink)

        self.sites.facilities = sorted(facilities, key=attrgetter('last_modified'))

    def get_sites(self, last_ran=datetime.min):
        """returns a dictionary mapping URLs as keys to the date that flm was last
        modified as a value.

        *   ``last_ran`` - a datetime object, with the time given as UTC time, with
            which to search for last_modified times after. defaults to
            ``datetime.min``, that is, to return all FacilityLinks.
        """


        if not last_ran:
            last_ran = datetime.min

        return dict((link.xlink_href, link.last_modified)
                    for link in self.sites.facilities
                    if link.last_modified >= last_ran)


class FacilityParser(object):
    """A class to parse a single FLM feed.

    Keyword arguments:
    xml -- an xml string or an open, readable xml file containing an FLM feed.

    """
	def __init__(self, xml=''):
		self.contents = xml
		flm = BeautifulSoup(self.contents, 'xml')

		if flm.FLMPartial and flm.FLMPartial.get_text().lower() == "true":
			pass # Warning for partial FLM?

		self.facility = Facility(flm)

	# Add some more consuming methods, these are just ideas of what data you'd need to get back.
	def get_screens(self):
        """Returns the dictionary of screens in a facility keyed by screen number."""
		return self.facility.auditoriums

	def get_certificates(self):
        """Returns all certificates for all of the screens in the facility."""
		screens = {}

		for key in self.facility.auditoriums:
			auditorium = self.facility.auditoriums[key]

			certs = []
			for device in auditorium.devices:
				certs.append(device.certificates)

			screens[key] = certs

		return screens

class Facility(object):
    """Represents the top-level facility which the FLM refers to.

    Mandatory fields (guaranteed to not be ``None`` for a valid FLM):
    id -- The facility's unique ID
    name -- The name of the facility
    circuit -- The circuit (exhibitor) the facility belongs to
    addresses -- A dictionary of the addresses for the facility.
        There can be any combination of a *physical*, *shipping* or a *billing* address but there must be at least one.
    auditoriums -- The screens in a facility

    Optional fields (may be ``None`` or empty):
    alternate_ids -- A list of alternate IDs (also unique) for the facility
    booking_partner_id -- The ID of the facility's booking partner
    timezone -- The time zone name of the facility in TZ format
    contacts -- A list of people or organisations who are contacts for the facility

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
			for contact in contact_list("Contact"):
				self.contacts.append(Contact(contact))

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

    The address of a facility can be *physical*, *shipping* or *billing*.

    Mandatory fields:
    street_address -- The street line of the address
    city -- The city of the address
    province -- The province/state/county of the address
    country -- The two letter ISO3166 country code where the address resides

    Optional fields:
    addressee -- The contact whom the address refers to
    street_address2 -- The second line of the street in the address
    postal_code -- The postal/zip code of the address

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
    number -- The number of the auditorium in the facility
    supports_35mm -- Whether the auditorium supports 35mm film or not
    devices -- The devices present in the auditorium

    Optional fields:
    name -- The name of the auditorium (eg. "Auditorium 1")
    screen_aspect_ratio -- The aspect ratio of the screen.
        Possible values are 1.85, 2.39, 1.66, 1.37 or other.
    adjustable_screen_mask -- The type of the adjustable screen mask.
        Possible values are top, side, both or none.
    audio_format -- The audio format in the auditorium (eg. "5.1")
    install_date -- The install date of the auditorium
    large_format_type -- The large format type of the auditorium
    digital_3d_system -- The 3D system installed in the auditorium

    """
	def __init__(self, auditorium):
		self.number = uint(auditorium.AuditoriumNumber)
		self.name = string(auditorium.AuditoriumName)

		self.supports_35mm = boolean(auditorium.Supports35MM)
		self.screen_aspect_ratio = string(auditorium.ScreenAspectRatio) # enum
		self.adjustable_screen_mask = string(auditorium.AdjustableScreenMask) # enum
		self.audio_format = string(auditorium.AudioFormat)
		# self.install_date = datetime(auditorium.AuditoriumInstallDate)
		self.large_format_type = string(auditorium.LargeFormatType)

		if auditorium.Digital3DSystem:
			self.digital_3d_system = Digital3DSystem(auditorium.digital_3d_system)

		self.devices = []
		for device in auditorium.DeviceGroupList("Device"):
			self.devices.append(Device(device))


class Contact(object):
    """Represents a point of contact.

    Mandatory fields:
    name -- The name of the contact

    Optional fields:
    country -- The ISO3166 country code for the contact
    phone1 -- First phone number for the contact
    phone2 - Second phone number for the contact
    email -- Email address for the contact
    type -- A string categorising the contact

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
    type -- The type of the device defined by SMPTE 433-2008
    id -- A unique ID for the device.  This can be a UUID or a certificate thumbprint.
    manufacturer_name -- The name of the device manufacturer
    model_number -- The model number of the device
    active -- Whether the device is currently in active use or not

    Optional fields:
    serial -- The serial number of the device
    manufacturer_id -- A URI corresponding to the ID of the manufacturer
    install_date -- The device install date
    resolution -- The resolution of the device (if a playback device)
        Possible values are 2K, 4K and other.
    integrator -- The integrator for the device
    vpf_finance_entity -- The entity responsible for VPF on the device
    vpf_start_date -- The date from which VPF was established on the device
    ip_addresses -- Contactable IPv4/IPv6 addresses for the device
    software -- A list of installed software on the device
    certificates -- A list of certificates associated with the device
    watermarking -- Watermarks associated with the device
    kdm_deliveries -- A list of methods for delivery of KDMs to the device
    dcp_deliveries -- A list of methods for delivery of DCP content to the device
        Delivery methods are email, modem, network or physical.

    """
	def __init__(self, device):
        """Represents a device in an auditorium.

        Mandatory fields:
        type -- The type of the device defined by SMPTE 433-2008
        id -- A unique ID for the device.  This can be a UUID or a certificate thumbprint.
        manufacturer_name -- The name of the device manufacturer
        model_number -- The model number of the device
        active -- Whether the device is currently in active use or not

        Optional fields:
        serial -- The serial number of the device
        manufacturer_id -- A URI corresponding to the ID of the manufacturer
        install_date -- The device install date
        resolution -- The resolution of the device (if a playback device)
            Possible values are 2K, 4K and other.
        integrator -- The integrator for the device
        vpf_finance_entity -- The entity responsible for VPF on the device
        vpf_start_date -- The date from which VPF was established on the device
        ip_addresses -- Contactable IPv4/IPv6 addresses for the device
        software -- A list of installed software on the device
        certificates -- A list of certificates associated with the device
        watermarking -- Watermarks associated with the device
        kdm_deliveries -- A list of methods for delivery of KDMs to the device
        dcp_deliveries -- A list of methods for delivery of DCP content to the device
            Delivery methods are email, modem, network or physical.

        """
		#  Device Types (SMPTE 433-2008)
		# DEC  Media Decoder
		# FMI  Forensic Mark Inserter (Image/Picture)
		# FMA  Forensic Mark Inserter (Audio/Sound)
		# LD   Link Decryptor (Image/Picture)
		# LE   Link Encryptor (Image/Picture)
		# MDA  Media Decryptor (Audio/Sound)
		# MDI  Media Decryptor (Image/Picture)
		# MDS  Media Decryptor (Subtitle)
		# NET  Networking Device
		# PLY  Playback Device
		# PR   Projector
		# PWR  Power Control System
		# SM   Security Manager
		# SMS  Screen Management System
		# SPB  Secure Processing Block
		# TAS  Theater Automation System
		# TMS  Theater Management System
		self.type = string(device.DeviceTypeID)
		self.id = string(device.DeviceIdentifier)
		self.serial = string(device.DeviceSerial)
		self.manufacturer_id = string(device.ManufacturerID)
		self.manufacturer_name = string(device.ManufacturerName)
		self.model_number = string(device.ModelNumber)
		# self.install_date = datetime(device.InstallDate.get_text())
		self.resolution = string(device.Resolution)
		self.active = boolean(device.IsActive)

		self.integrator = string(device.Integrator)
		self.vpf_finance_entity = string(device.VPFFinanceEntity)
		self.vpf_start_date = None
		if device.VPFStartDate:
			self.vpf_start_date = date(device.VPFStartDate)

		self.ip_addresses = []
		if device.IPAddressList:
			for ip_address in device.IPAddressList("IPAddress"):
				self.ip_addresses.append(IPAddress(ip_address))

		self.software = []
		if device.SoftwareList:
			for program in device.SoftwareList("Software"):
				self.software.append(Software(program))

		self.certificates = []
		if device.KeyInfoList:
			for certificate in device.KeyInfoList("X509Data"):
				self.certificates.append(Certificate(certificate))

        self.watermarking = []
        if device.WatermarkingList:
            for watermark in device.WatermarkingList("Watermarking"):
                self.watermarking.append(Watermarking(watermark))

		self.kdm_deliveries = deliveries(device.KDMDeliveryMethodList)
		self.dcp_deliveries = deliveries(device.DCPDeliveryMethodList)

class Digital3DSystem(object):
    """Represents a digital 3D system installed in an auditorium.

    Mandatory fields:
    active -- Whether the 3D system is active or not
    
    Optional fields:
    configuration -- A string describing the 3D configuration, eg. "RealD" or "Dolby 3D"
    install_date -- The install date of the 3D system
    screen_color -- The colour of the screen.
        Possible values are silver, white or other.
    screen_luminance -- The luminance of the screen.
        Possible values are between 1 and 29 (inclusive).
    ghostbusting -- Whether the screen supports ghostbusting technology
    ghostbusting_configuration -- Details of the ghostbusting configuration

    """
	def __init__(self, system):
		self.active = boolean(auditorium.IsActive)
		self.configuration = string(auditorium.Digital3DConfiguration)
		# self.install_date = datetime(auditorium.InstallDate.get_text())
		self.screen_color = string(auditorium.ScreenColor) # enum
		self.screen_luminance = uint(auditorium.ScreenLuminance) # 1 to 30
		self.ghostbusting = boolean(auditorium.ghostbusting)
		self.ghostbusting_configuration = string(auditorium.GhostbustingConfiguration)

class IPAddress(object):
    """Represents an IPv4 or IPv6 address.

    Mandatory fields:
    address -- The IP address

    Optional fields:
    host -- The hostname

    """
	def __init__(self, ip_address):
		self.address = string(ip_address.Address)
		self.host = string(ip_address.Host)

class Software(object):
    """Represents a version of a device.

    This can be used to describe any versionable portion of a device, and not just software.

    Mandatory fields:
    description -- A description of the software (such as the name)
    version -- The software version

    Optional fields:
    kind -- The type of the software.
        Possible values are firmware, software or hardware.
    producer -- The software producer
    filename -- The name of the file
    file_size -- Size of the file
    file_time -- The creation or last modified time of the file

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
    name -- The X509 subject name
    certificate -- The X509 certificate

    """
	def __init__(self, cert):
		self.name = string(cert.X509SubjectName)
		self.certificate = string(cert.X509Certificate)

class Watermarking(object):
    """Represents information about watermarking associated with a device.

    Mandatory fields:
    manufacturer -- The watermarking manufacturer
    
    Optional fields:
    kind -- The type of watermarking.
        Possible values are picture or audio.
    model -- The model of the watermarking system
    version -- The version of the watermarking system

    """
	def __init__(self, watermarking):
		self.manufacturer = string(watermarking.WatermarkManufacturer)
		self.kind = string(watermarking.WatermarkKind) # enum
		self.model = string(watermarking.WatermarkModel)
		self.version = string(watermarking.WatermarkModel)
