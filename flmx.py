from datetime import datetime
import beautifulsoup4

class SiteListParser(object):
	def __init__(self, xml=''):
		self.contents = xml
		# Do some parsing

	def get_sites(last_ran=None):
		# Should be able to return the list of urls for a site list.
		# Also should be able to pass in a last_run datetime and have it return only the sites that have been modified since then.

		return [
			{"url": "/flmx/some-uuid", "last_modified": datetime.now()}
		]

class FacilityParser(object):
	def __init__(self, xml=''):
		self.contents = xml
		# Do some parsing

	# Add some more consuming methods, these are just ideas of what data you'd need to get back.
	def get_screens():
		pass

	def get_certificates():
		pass