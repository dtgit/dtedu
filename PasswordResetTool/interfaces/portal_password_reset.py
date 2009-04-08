# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# Written by J. Cameron Cooper

"""Fairly secure password reset interface"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_password_reset(Interface):
    """Defines an interface for a tool that provides a facility to
    reset forgotten passwords.

    This interface is rather sparse, but sufficient to describe the
    task. (In this manner we void being dependant on a specific
    process) The details of the process are in the implementation,
    where they belong."""

    id = Attribute('id','Must be set to "portal_password_reset"')

    def requestReset(userid):
        """Ask the system to start the password reset procedure for
        user 'userid'.

        Returns the random string that must be used to reset the
        password."""

    def resetPassword(userid, randomstring, password):
        """Set the password (in 'password') for the user who maps to
        the string in 'randomstring'. The 'userid' parameter is provided
        in case extra authentication is needed."""
