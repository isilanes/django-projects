# Classes:
class GeneralName(object):
    regex = '\w+'

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value