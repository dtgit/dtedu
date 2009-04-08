SecureMailHost
==============

SecureMailHost is a reimplementation of the standard MailHost with some security
and usability enhancements:

  * ESMTP login on the mail server based on the MailHost from 
    http://www.zope.org/Members/bowerymarc

  * Start TLS (ssl) connection if possible

  * Usage of Python 2.3's email package which has multiple benefits like easy to
    generate multi part messages including fance HTML emails and with images.

  * A new secureSend() method that seperates headers like mail to, mail from
    from the body text. You don't need to mingle body text and headers any more.

  * Email address validation based on the code form PloneTool for mail from,
    mail to, carbon copy and blin carbon copy to prevent spam attacks. 
    (Only for secureSend()!)

  * Message-Id and X-Mailer header generation to lower the spam hit points of
    Spam Assassin.

Author:
    Christian Heimes <tiran@cheimes.de>

License:
    ZPL 2.1

Downloads:
    http://plone.org/products/securemailhost

Bug collector:
    https://dev.plone.org/plone under component Mail
