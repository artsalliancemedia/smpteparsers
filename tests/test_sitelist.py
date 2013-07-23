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
        self.assertRaises(flmx.FlmxParseError, flmx.SiteListParser, self.malformedA)
        # value error as the modified field won't pass strptime
        self.assertRaises(flmx.FlmxParseError, flmx.SiteListParser, self.malformedB)

    def test_emptyxml(self):
        # will look for the attribute 'Originator', which ofc isn't there
        self.assertRaises(flmx.FlmxParseError, flmx.SiteListParser, self.empty)

class TestSiteListDateHandling(unittest.TestCase):
    def test_dates(self):
        #normal good date
        self.assertEqual(flmx.get_datetime('2012-01-13T12:30:00+00:00'),
                         datetime(2012, 1, 13, 12, 30, 0))
        #bad date (month 13)
        self.assertRaises(ValueError, flmx.get_datetime, '2012-13-13T12:30:00+00:00')

    def test_goodtimezones(self):        
        date = '2012-01-01T12:20:00'
        dt = datetime(2012, 1, 1, 12, 20, 0)
        #utc
        self.assertEqual(flmx.get_datetime(date + '-00:00'), dt)   
        self.assertEqual(flmx.get_datetime(date + '+00:00'), dt)   

        #positive timezone 
        self.assertEqual(flmx.get_datetime(date + '+01:30'),
                         dt - timedelta(hours=1, minutes = 30))
        #negative timezone 
        self.assertEqual(flmx.get_datetime(date + '-01:30'),
                         dt - timedelta(hours=-1, minutes = -30))

    def test_badtimezones(self):
        date = '2012-01-01T12:20:00'
        #invalid timezones
        self.assertRaises(ValueError, flmx.get_datetime, date + 'aaaaaa')
        self.assertRaises(ValueError, flmx.get_datetime, date + '+aa:aa')
        self.assertRaises(ValueError, flmx.get_datetime, date + '+15:a0')

class TestSiteListUnusualTimes(unittest.TestCase):
    def test_noMillis_noTimezone(self):
        # missing "+00:00" or similar
        self.assertEqual(flmx.get_datetime('2012-01-01T12:30:00'),
                         datetime(2012, 1, 1, 12, 30, 0))

    def test_millis_timezones(self):
        # with millis appended - just flooring that value for the moment
        self.assertEqual(flmx.get_datetime('2012-01-01T12:30:00.123+01:00'),
                         datetime(2012, 1, 1, 11, 30, 1))

    def test_millis_noTimezone(self):
        # with millis and no tz
        self.assertEqual(flmx.get_datetime('2012-01-01T12:30:00.123'),
                         datetime(2012, 1, 1, 12, 30, 1))


    def test_noColonTimezone(self):
        #timezone as +0000
        self.assertEqual(flmx.get_datetime('2012-01-01T12:30:00+0130'),
                         datetime(2012, 1, 1, 11, 00, 0))
        self.assertEqual(flmx.get_datetime('2012-01-01T12:30:00-0130'),
                         datetime(2012, 1, 1, 14, 00, 0))

    def test_noMinutesTimezone(self):
        #timezone as +00 (no minutes)
        self.assertEqual(flmx.get_datetime('2012-01-01T12:30:00+01'),
                         datetime(2012, 1, 1, 11, 30, 0))
        self.assertEqual(flmx.get_datetime('2012-01-01T12:30:00-01'),
                         datetime(2012, 1, 1, 13, 30, 0))

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

    def test_noDate(self):
        dict = self.sites.get_sites()
        self.assertEqual(len(dict), 3)
        #datetimes should be correct, given that TestSiteListDateHandling worked
        self.assertEqual(dict['linkA'], self.datetimeA)
        self.assertEqual(dict['linkB'], self.datetimeB)
        self.assertEqual(dict['linkC'], self.datetimeC)

    def test_middleDate(self):
        #beginning of 2012, should only return B and C
        dict = self.sites.get_sites(datetime(2012,01,01,12,0,0))
        self.assertEqual(len(dict), 2)
        self.assertFalse('linkA' in dict)
        self.assertEqual(dict['linkB'], self.datetimeB)
        self.assertEqual(dict['linkC'], self.datetimeC)

    def test_beforeDate(self):
        #beginning of 2011, should return all
        dict = self.sites.get_sites(datetime(2011,01,01,12,0,0))
        self.assertEqual(len(dict), 3)
        self.assertEqual(dict['linkA'], self.datetimeA)
        self.assertEqual(dict['linkB'], self.datetimeB)
        self.assertEqual(dict['linkC'], self.datetimeC)

    def test_middleDate(self):
        #beginning of 2014, should not return anything
        dict = self.sites.get_sites(datetime(2014,01,01,12,0,0))
        self.assertEqual(len(dict), 0)
