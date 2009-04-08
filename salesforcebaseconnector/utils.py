from datetime import datetime
from DateTime import DateTime

def DateTime2datetime(value):
    """Helper function returning appropriately converted
       Zope DateTime to Python datetime.
    """
    if value is None or isinstance(value, datetime):
        return value
    if not isinstance(value, DateTime):
        raise ValueError, "value must be an instance of DateTime"
    return datetime.fromtimestamp(value.timeTime())
