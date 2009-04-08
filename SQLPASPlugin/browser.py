from Products.CMFCore.utils import getToolByName

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile

from Products.SQLPASPlugin import utils, config


class ConfigletView(BrowserView):
    template_options = {
        'setup':
        ZopeTwoPageTemplateFile('configlet-setup.pt'),
        'configure':
        ZopeTwoPageTemplateFile('configlet-configure.pt'),
        }

    def _set_context(self, context):
        self._context = [context]
    def _get_context(self):
        return self._context[0]
    context = property(_get_context, _set_context)

    def __call__(self):
        if self.request.get('form.submit', 0):
            if not self.is_setup():
                return self.handle_setup()
            else:
                return self.handle_config()
        else:
            return self.template()

    def template(self):
        template = self.template_options[
            self.is_setup() and 'configure' or 'setup']
        return template
    template = property(template)

    def handle_setup(self):
        conn = self.request.get('form.conn', '')
        if not conn:
            self.request['portal_status_message'] = (
                "Please choose a connection.")
            return self.template()
        else:
            utils.updatePAS(
                getToolByName(self.context, 'portal_url').getPortalObject(),
                sql_connection=conn)
            assert self.is_setup()
            # Instead of returning self.template() I have to redirect
            # here because otherwise the test would complain about an
            # unauthorized context (the 'view' may not be accessed by
            # the page template).
            return self.request.response.redirect(
                self.request['URL0'] +
                '?portal_status_message=Setup+successful.')

    def handle_config(self):
        schema = dict(users_table="User table",
                      users_col_username="User column",
                      users_col_password="Password column")
        variables = {}
        for name, title in schema.items():
            variables[name] = self.request.get(name, '')
            if not variables[name]:
                msg = ("Missing value for %s."%schema[name]).replace(' ', '+')
                return self.request.response.redirect(
                    self.request['URL0'] +
                    '?portal_status_message=%s' % msg)

        for plugin in self.plugins:
            plugin.manage_changeProperties(**variables)
        self.request['portal_status_message'] = (
            "Configuration successful!  Please check Zope's log for any error "
            "messages.")
        return self.template()

    def is_setup(self):
        uf = getToolByName(self.context, 'acl_users')
        usermanager = getattr(uf, config.USERMANAGER_ID, None)

        if (self.get_connections() and usermanager
            and usermanager.meta_type == 'SQL User Manager'
            and self.have_all_plugins()):
            # Also check if plugins have valid connections,
            # i.e. if the connection objects still exist.
            for plugin in self.plugins:
                if getattr(plugin, plugin._connection, None) is None:
                    return False
            else:
                return True

    def get_connections(self):
        return [dict(id=conn[0], title=conn[1])
                for conn in self.context.SQLConnectionIDs()]

    def plugins(self):
        uf = getToolByName(self.context, 'acl_users')
        return (getattr(uf, config.USERMANAGER_ID, None),
                getattr(uf, config.PROPERTYPROVIDER_ID, None))
    plugins = property(plugins)

    def have_all_plugins(self):
        return None not in self.plugins

    def have_one_plugin(self):
        return filter(None, self.plugins)

    def _get_usertable(self):
        return self.plugins[0].getProperty('users_table')
    def _set_usertable(self, value):
        for plugin in self.plugins:
            plugin.manage_changeProperties(users_table=value)
    usertable = property(_get_usertable, _set_usertable)

    def _get_usercol(self):
        return self.plugins[0].getProperty('users_col_username')
    def _set_usercol(self, value):
        for plugin in self.plugins:
            plugin.manage_changeProperties(users_col_username=value)
    usercol = property(_get_usercol, _set_usercol)

    def _get_passcol(self):
        return self.plugins[0].getProperty('users_col_password')
    def _set_passcol(self, value):
        for plugin in self.plugins:
            plugin.manage_changeProperties(users_col_password=value)
    passcol = property(_get_passcol, _set_passcol)
