.. currentmodule:: flmx.__init__

FLM-x Parser
============

The FLM-x parser is an API to process, validate and manipulate FLM-x feeds.
For more information on the FLM-x format, including examples and schema documents, see the `FLM-x Homepage`__.

The parser can be called directly to retrieve an FLM site list and iterate through it.
It will get all the individual FLMs from the site list, and return FacilityParser
objects which contain all the information for each facility.

Basic usage:

>>> from smpteparsers import flmx
>>> facilities = flmx.parse('http://example.com/FLMX.xml')
>>> # Process FacilityParser objects as necessary

.. autofunction:: parse

More information on the components which make up the FLM-x parser can be found on the
individual module pages below:

.. toctree::

   sitelistparser
   facilityparser
   xmlvalidator


.. __: http://flm.foxpico.com/