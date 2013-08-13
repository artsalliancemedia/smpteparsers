.. module:: flmx.facility

================================
Facility Parser
================================

The Facility Parser takes an FLM and parses it into memory as python objects.
It contains a range of convenience methods to access the data from the XML document.

Example usage:

>>> # Open file handle
... with open(u'flm.xml') as flm:
...   # Set up FacilityParser
...   fp = flmx.FacilityParser(flm)
...   # Get certificates
...   certs = fp.get_certificates()
...   # Print out the certificates for screen #3 (for example)
...   print(certs[3])

.. autoclass:: FacilityParser
   :members:

Objects
--------------------------------

.. autoclass:: Address
.. autoclass:: Auditorium
.. autoclass:: Certificate
.. autoclass:: Contact
.. autoclass:: Device
.. autoclass:: Digital3DSystem
.. autoclass:: IPAddress
.. autoclass:: Software
.. autoclass:: Watermarking
