class FlmxError(Exception):
    u"""Base exception that all Flmx errors extend for easy catching.
    """
    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return 'FlmxError' + self.msg

class FlmxCriticalError(FlmxError):
    u"""A critical error that cannot be resolved, causing program running to stop.

    For example, is thrown when there is a problem with the local schema xsd files.
    """
    pass

class FlmxParseError(FlmxError):
    u"""An exception that is raised when an error is encountered within the validation of the xml document
    against its schema.

    Indicates that the XML is invalid, and will be ignored.
    """
    pass

class FlmxPartialError(FlmxError):
    u"""This exception is raised for partial FLMs with the FLMPartial flag set to true.

    According to the FLM specification draft, this flag is never used.  But in
    the unlikely event that a single FLM is split into multiple parts, the application
    is not able to handle this so an error is thrown.

    """
    pass
