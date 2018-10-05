# Classes:
class GeneralName(object):
    regex = '\w+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


class DateStamp(object):
    """Datestamp in YYYYMMDDHHmm format."""
    regex = '\d+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value

class NameWithSpaces(object):
    regex = '\w[\w ]+\w'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value
