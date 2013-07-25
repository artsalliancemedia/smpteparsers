from flmx import facility, sitelist
from datetime import datetime
import requests

# FLM-x shortcut parser
def parse_flmx(self, sitelist_url, username='', password='', last_ran=datetime.min):

    # Get sitelist from URL using authentication if necessary
    res = None
    if username and password:
        res = requests.get(sitelist_url, auth=(username, password))
    else:
        res = requests.get(sitelist_url)

    self.sp = sitelist.SiteListParser(res.text)

    facilities = []

    for site in self.sp.get_sites(last_ran)
        res = None
        if self.username and self.password:
            res = requests.get(self.url + site, auth=(self.username, self.password))
        else:
            res = requests.get(self.url + site)

        fp = facility.FacilityParser(res.text)
        facilities.append(fp)

    return facilities
