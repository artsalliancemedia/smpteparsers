import flmx
import unittest
from datetime import datetime


class TestSiteListParser(unittest.TestCase):

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

    # cuts off part-way through facility
    malformed = """
        <SiteList xmlns="http://isdcf.com/2010/04/SiteList" xmlns:xlink="http://www.w3.org/1999/xlink">
            <Originator>orig</Originator>
            <SystemName>sysName</SystemName>
            <DateTimeCreated>2001-01-01T15:49:40.220</DateTimeCreated>
            <FacilityList>
                <Facility id="A" modified="2011-04-07T12:10:01-00:00" xlink:href="linkC" xlink:type="simple"/>
                <Facility id="B" modified="2012-05-08T12:11:02-01:20" xlink:href="linkB" xlink:type="simple"/>
                <Facility id="C" modified="2013-06-09T12:11:02-01:20" 
        """


    def test_goodxml(self):
        s = flmx.SiteListParser(self.good)
        dict = s.get_sites()
        self.assertEqual(len(dict), 3)

    def test_malformedxml(self):
        # will look for the key originator, and raise a keyerror
        self.assertRaises(AttributeError, flmx.SiteListParser, self.empty)

    def test_emptyxml(self):
        # will look for the key xlink:href in FacilityList , and raise a keyerror
        self.assertRaises(KeyError, flmx.SiteListParser, self.malformed)

    
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSiteListParser)
    unittest.TextTestRunner(verbosity=2).run(suite)