[![Build Status](https://travis-ci.org/artsalliancemedia/smpteparsers.png)](http://travis-ci.org/artsalliancemedia/smpteparsers)

## smpteparsers

Set of classes for grabbing digital cinema documents in xml format and loading them into nice python objects.

### Installation

**Prerequisites: **

* Python 2.6.x (2.7.x should work though)
* pip

After grabbing the code run the following to install any dependencies:

```
pip install -r requirements.txt
```
---------------------------------------

### FLMX 

The FLMX suite is used to create objects from FLM-x feeds, as specified on the [FLM-x Homepage](http://flm.foxpico.com/).

#### Usage

##### Typical usage

To parse a non-protected site-list XML file, and then fetch all keys for all cinemas that its constituent FLM files contain, do the following:

    from smpteparsers import flmx
    
    facilities = flmx.parse(u'http://example.com/FLMX.xml')
    
    for facility in facilities:
        screen_keys = facility.get_certificates()
    
        print(screen_keys)
    # can expect to see: {'screen 1', 'ABC123', ....}

where `facility` is a *Facility* object, as defined in `facility.py`. *Facility* contains a variety of member variables to help you access any of the data contained within it.

##### Other options

To parse and manipulate the sitelist on its own, you must instead use the `SiteListParser` object, or if you already have an FLM file, you can use the `FacilityParser` object.

Please refer to the full documentation for all details on the composition of these classes and objects.

---------------------------------------

#### Documentation

Full documentation is provided with [Sphinx](http://sphinx-doc.org/). To generate the documentation using a commmand prompt or terminal, navigate to `/doc/`, and then call `make html`. Sphinx provides many other formats to build in (by calling `make` followed by a keyword), including `text`, `latex`, `man` and more. Please see the Sphinx website for more suggestions. The documentation can then be viewed by navigating to `/doc/_build/html`, and then opening `index.html`


#### Testing

Run `nosetests` from the root directory :)
