"""
Uses Roberto A. F. De Almeida's http://dealmeida.net/ module to do its handy work

author: Tom Lazar <tom@tomster.org> at the archipelago sprint 2006

"""

from Products.PortalTransforms.interfaces import itransform
from Products.PortalTransforms.libtransforms.utils import bin_search, sansext
from Products.PortalTransforms.libtransforms.commandtransform import commandtransform
from Products.CMFDefault.utils import bodyfinder
import os

try:
    import textile as textile_transformer
except ImportError:
    HAS_TEXTILE = False
else:
    HAS_TEXTILE = True
    

class textile:
    __implements__ = itransform

    __name__ = "textile_to_html"
    inputs  = ("text/x-web-textile",)
    output = "text/html"

    def name(self):
        return self.__name__

    def convert(self, orig, data, **kwargs):
        if HAS_TEXTILE:
            html = textile_transformer.textile(orig, encoding='utf-8', output='utf-8')
        else:
            html = orig
        data.setData(html)
        return data

def register():
    return textile()
