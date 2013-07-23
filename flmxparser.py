from flmx import facility, sitelist
from datetime import datetime
import requests, json

# FLM-x shortcut parser
class Flmx(object):
    def __init__(self, settings_file):
        settings = {}
        with open(settings_file) as fp:
            settings = json.load(fp)

        self.url = settings['url']
        self.username = settings.get('username')
        self.password = settings.get('password')

        res = None
        if self.username and self.password:
            res = requests.get(self.url, auth=(self.username, self.password))
        else:
            res = requests.get(self.url)

        self.sp = sitelist.SiteListParser(res.text)

        # Get all the sites
        # This can be changed if we can get the last_ran time from a db
        self.sites = self.sp.get_sites()
        self.last_ran = datetime.now()

    def get_updated_sites(self):
        # This will overwrite the sites with only the ones updated since the last run
        self.sites = self.sp.get_sites(self.last_ran)
        self.last_ran = datetime.now()

    def get_certificates(self):
        facilities = {}

        # Gets all the certificates
        # With db connection update to yield certificates
        for site in self.sites:
            res = None
            if self.username and self.password:
                res = requests.get(self.url + site, auth=(self.username, self.password))
            else:
                res = requests.get(self.url)

            fp = facility.FacilityParser(res.text)
            certs = fp.get_certificates()
            facilities[fp.facility.id] = certs

        return facilities

def main():
    flmx = Flmx("settings.json")
    certs = flmx.get_certificates()
    print(certs)

if __name__ == "main":
    main()