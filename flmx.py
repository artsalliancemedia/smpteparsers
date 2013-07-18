from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from operator import attrgetter

def get_datetime(isoDate):
	#: returns the utc datetime for a given ISO8601 date string formatted
	#: YYYY-mm-ddTHH:MM:SSZ, where Z is a timezone given as +/-HHMM
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
	id_code = "" 
	last_modified = datetime.min
	xlink_href = "" 
	xlink_type = "simple" 

	def __str__(self):
		return 'FacilityLink: \
				id: ' + self.id_code + ', \
				modified: ' + self.last_modified.strftime('%Y-%m-%dT%H:%M:%S') + ' \
				link_href: ' + self.xlink_href + ' \
				link_type: ' + self.xlink_type


class SiteList(object):
	originator = ""
	systemName = ""
	facilities = []

class SiteListParser(object):
	sites = SiteList()
	def __init__(self, xml=''):
		self.contents = xml

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

	#: last_ran must be UTC
	def get_sites(self, last_ran=None):
		# Should be able to return the list of urls for a site list.
		# Also should be able to pass in a last_run datetime and have it return only the sites that have been modified since then.
		if not last_ran:
			last_ran = datetime.min

		return dict((link.xlink_href, link.last_modified)
					for link in self.sites.facilities
					if link.last_modified >= last_ran)


class FacilityParser(object):
	def __init__(self, xml=''):
		self.contents = xml
		# Do some parsing

	# Add some more consuming methods, these are just ideas of what data you'd need to get back.
	def get_screens():	
		pass

	def get_certificates():
		pass

