"""
$Id: Domain.py 21785 2006-04-04 20:34:35Z hannosch $
"""

class Domain:

    def __init__(self, domain, service):
        self._domain = domain
        self._translationService = service

    def getDomainName(self):
        """Return the domain name"""
        return self._domain

    def translate(self, msgid, mapping=None, context=None,
                  target_language=None):
        return self._translationService.translate(
            self._domain, msgid, mapping, context, target_language)
