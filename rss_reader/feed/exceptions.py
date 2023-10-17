class FeedException(Exception):
    details = "Error while parsing feed"

    def __init__(self, details=None, context=None):
        self.details = details or self.default_details
        self.context = context
