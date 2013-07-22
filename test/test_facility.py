import flmx
import unittest2 as unittest
from bs4 import BeautifulSoup

class TestFacilityParser(unittest.TestCase):

    def setUp(self):
        self.f = open('test/testFLM.xml')
        self.xml = self.f.read()
        self.fp = flmx.FacilityParser(self.xml)

    def tearDown(self):
        self.f.close()

    def test_get_screens(self):
        screens = self.fp.get_screens()

        # Auditorium object created directly using constructor
        auditorium = flmx.Auditorium(BeautifulSoup(self.xml, 'xml').Auditorium)

        # Check two objects have same values for all fields
        self.assertEqual(screens[1].number, auditorium.number)
        self.assertEqual(screens[1].supports_35mm, auditorium.supports_35mm)
        self.assertEqual(screens[1].name, auditorium.name)
        self.assertEqual(screens[1].screen_aspect_ratio, auditorium.screen_aspect_ratio)
        self.assertEqual(screens[1].adjustable_screen_mask, auditorium.adjustable_screen_mask)
        self.assertEqual(screens[1].audio_format, auditorium.audio_format)
        self.assertEqual(screens[1].install_date, auditorium.install_date)
        self.assertEqual(screens[1].large_format_type, auditorium.large_format_type)

    def test_get_certificates(self):
        certs = self.fp.get_certificates()

        soup = BeautifulSoup(self.xml, 'xml')("Auditorium")
        for auditorium in soup:
            screen_index = None
            if auditorium.AuditoriumNumber:
                screen_index = int(auditorium.AuditoriumNumber.get_text())
            elif auditorium.AuditoriumName:
                screen_index = auditorium.AuditoriumName.get_text()
            else:
                self.fail()

            for i, cert_xml in enumerate(auditorium("X509Data")):
                # Make certificate object directly from XML snippet
                cert = flmx.Certificate(cert_xml)

                self.assertEqual(certs[screen_index][i].name, cert.name)
                self.assertEqual(certs[screen_index][i].certificate, cert.certificate)
