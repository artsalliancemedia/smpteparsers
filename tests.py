import flmx
import unittest
from datetime import datetime, timedelta

class TestSiteListXMLParsing(unittest.TestCase):

    good = """
        <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
            <Originator>orig</Originator>
            <SystemName>sysName</SystemName>
            <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
            <FacilityList>
                <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkC" xlink:type="simple"/>
                <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple"/>
                <Facility id="C" modified="2013-06-09T12:12:03+03:40" xlink:href="linkA" xlink:type="simple"/>
            </FacilityList>
        </SiteList>
        """

    empty = """ 
            
            """

    nofacilities = """
                    <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
                        <Originator>orig</Originator>
                        <SystemName>sysName</SystemName>
                        <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
                        <FacilityList>
                        </FacilityList>
                    </SiteList>
                    """

    # cuts off part-way through facility
    malformedA = """
        <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
            <Originator>orig</Originator>
            <SystemName>sysName</SystemName>
            <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
            <FacilityList>
                <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkC" xlink:type="simple"/>
                <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple"/>
                <Facility id="C" modified="2013-06-09T12:11:02-01:20" 
        """
    # cuts off part-way through a date field
    malformedB = """
        <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
            <Originator>orig</Originator>
            <SystemName>sysName</SystemName>
            <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
            <FacilityList>
                <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkC" xlink:type="simple"/>
                <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple"/>
                <Facility id="C" modified="2013-06-09T12: 
        """

    def test_goodxml(self):
        s = flmx.SiteListParser(self.good)
        dict = s.get_sites()
        self.assertEqual(len(dict), 3)

    def test_malformedxml(self):
        # will look for the key xlink , and raise a keyerror
        self.assertRaises(KeyError, flmx.SiteListParser, self.malformedA)
        # value error as the modified field won't pass strptime
        self.assertRaises(ValueError, flmx.SiteListParser, self.malformedB)

    def test_emptyxml(self):
        # will look for the attribute 'Originator', which ofc isn't there
        self.assertRaises(AttributeError, flmx.SiteListParser, self.empty)

class TestSiteListDateHandling(unittest.TestCase):
    def test_dates(self):
        #normal good date
        self.assertEqual(flmx.get_datetime('2012-01-13T12:30:00+00:00'),
                         datetime(2012, 1, 13, 12, 30, 0))
        #bad date (month 13)
        self.assertRaises(ValueError, flmx.get_datetime, '2012-13-13T12:30:00+00:00')


    def test_timezones(self):
        date = '2012-01-13T12:30:00'
        dt = datetime(2012, 1, 13, 12, 30, 0)
        #positive timezone
        self.assertEqual(flmx.get_datetime(date + '+01:20'),
                         dt + timedelta(hours=1, minutes = 20))
        #negative timezone
        self.assertEqual(flmx.get_datetime(date + '-01:20'),
                         dt + timedelta(hours=-1, minutes = -20))

        #invalid timezones
        self.assertRaises(ValueError, flmx.get_datetime, date + 'aaaaaa')
        self.assertRaises(ValueError, flmx.get_datetime, date + '+aa:aa')

class TestSiteListFetchHandling(unittest.TestCase):
    goodxml = """
        <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
            <Originator>orig</Originator>
            <SystemName>sysName</SystemName>
            <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
            <FacilityList>
                <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkA" xlink:type="simple"/>
                <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple"/>
                <Facility id="C" modified="2013-06-09T12:12:03+03:40" xlink:href="linkC" xlink:type="simple"/>
            </FacilityList>
        </SiteList>
        """

    datetimeA = flmx.get_datetime('2011-04-07T12:10:01-00:00')
    datetimeB = flmx.get_datetime('2012-05-08T12:11:02-01:20')
    datetimeC = flmx.get_datetime('2013-06-09T12:12:03+03:40')

    def setUp(self):
        self.sites = flmx.SiteListParser(self.goodxml)

    def test_goodValues(self):
        dict = self.sites.get_sites()
        self.assertEqual(len(dict), 3)
        #datetimes should be correct, given that TestSiteListDateHandling worked
        self.assertEqual(dict['linkA'], self.datetimeA)
        self.assertEqual(dict['linkB'], self.datetimeB)
        self.assertEqual(dict['linkC'], self.datetimeC)

    def test_goodPartialValues(self):
        dict = self.sites.get_sites()


    
if __name__ == '__main__':
    unittest.main()
