try:
    from Products.validation.interfaces.IValidator import IValidator
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.pardir))
    from interfaces.IValidator import IValidator
    del sys, os

class RangeValidator:
    __implements__ = IValidator

    def __init__(self, name, minval=0.0, maxval=0.0, title='', description=''):
        self.name = name
        self.minval = minval
        self.maxval = maxval
        self.title = title or name
        self.description = description

    def __call__(self, value, *args, **kwargs):
        if len(args)>=1:
            minval=args[0]
        else:
            minval=self.minval
            
        if len(args)>=2:
            maxval=args[1]
        else:
            maxval=self.maxval

        assert(minval <= maxval)
        try:
            nval = float(value)
        except ValueError:
            return ("Validation failed(%(name)s): could not convert '%(value)r' to number" %
                    { 'name' : self.name, 'value': value})
        if minval <= nval < maxval:
            return 1

        return ("Validation failed(%(name)s): '%(value)s' out of range(%(min)s, %(max)s)" %
                { 'name' : self.name, 'value': value, 'min' : minval, 'max' : maxval,})
