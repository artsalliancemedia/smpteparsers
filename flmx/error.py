class FlmxParseError(Exception):
    """An exception that is raised when an error is encountered within the validation of the xml document
    against its schema.

    :param value: The contained error message object or string.

    """

    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return self.msg

class FlmxPartialError(Exception):
    """This exception is raised for partial FLMs with the FLMPartial flag set to true.

    According to the FLM specification draft, this flag is never used.  But in
    the unlikely event that a single FLM is split into multiple parts, the application
    is not able to handle this so an error is thrown.

    :param value: The contained error message object or string.

    """
    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return self.msg
