class FlmxParseError(Exception):
    """An exception that is raised when an error is encountered within the validation of the xml document
    against its schema.

    :param value: The contained error message object or string.

    """

    def __init__(self, value):
        self.msg = value

    def __str__(self):
        return self.msg
