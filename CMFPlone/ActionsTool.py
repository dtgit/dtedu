from AccessControl import ClassSecurityInfo
from Globals import InitializeClass
from Products.CMFCore.ActionInformation import ActionInfo
from Products.CMFCore.ActionsTool import ActionsTool as BaseTool
from Products.CMFCore.interfaces import IActionProvider
from Products.CMFPlone import ToolNames
from Products.CMFPlone.PloneBaseTool import PloneBaseTool


class ActionsTool(PloneBaseTool, BaseTool):

    meta_type = ToolNames.ActionsTool
    toolicon = 'skins/plone_images/confirm_icon.gif'

    __implements__ = (PloneBaseTool.__implements__, BaseTool.__implements__, )

    security = ClassSecurityInfo()

    #
    #   ActionProvider interface
    #
    security.declarePrivate('listActions')
    def listActions(self, info=None, object=None,
                    categories=None, ignore_categories=None):
        """ List all the actions defined by a provider.
        """
        actions = list(self._actions)

        if ignore_categories is None:
            ignore_categories = ()

        if categories is None:
            categories = [cat for cat in self.objectIds()
                              if cat not in ignore_categories]
        else:
            categories = [cat for cat in self.objectIds()
                              if cat in categories]

        for category in categories:
            actions.extend(self[category].listActions())
        return tuple(actions)

    security.declarePublic('listActionInfos')
    def listActionInfos(self, action_chain=None, object=None,
                        check_visibility=1, check_permissions=1,
                        check_condition=1, max=-1,
                        categories=None, ignore_categories=None):
        # List ActionInfo objects.
        # (method is without docstring to disable publishing)
        #
        ec = self._getExprContext(object)
        actions = self.listActions(object=object,
                                   categories=categories,
                                   ignore_categories=ignore_categories)
        actions = [ ActionInfo(action, ec) for action in actions ]

        if action_chain:
            filtered_actions = []
            if isinstance(action_chain, basestring):
                action_chain = (action_chain,)
            for action_ident in action_chain:
                sep = action_ident.rfind('/')
                category, id = action_ident[:sep], action_ident[sep+1:]
                for ai in actions:
                    if id == ai['id'] and category == ai['category']:
                        filtered_actions.append(ai)
            actions = filtered_actions

        if categories is not None:
            actions = [ai for ai in actions
                          if ai['category'] in categories]

        if ignore_categories is not None:
            actions = [ai for ai in actions
                          if ai['category'] not in ignore_categories]

        action_infos = []
        for ai in actions:
            if check_visibility and not ai['visible']:
                continue
            if check_permissions and not ai['allowed']:
                continue
            if check_condition and not ai['available']:
                continue
            action_infos.append(ai)
            if max + 1 and len(action_infos) >= max:
                break
        return action_infos

    #
    #   'portal_actions' interface methods
    #
    security.declarePublic('listFilteredActionsFor')
    def listFilteredActionsFor(self, object=None,
                               ignore_providers=(),
                               ignore_categories=None):
        """ List all actions available to the user.
        """
        actions = []

        providers = [name for name in self.listActionProviders()
                          if name not in ignore_providers]

        # Include actions from specific tools.
        for provider_name in providers:
            provider = getattr(self, provider_name, None)
            # Skip missing action providers.
            if provider is None:
                continue
            if IActionProvider.providedBy(provider):
                if provider_name == 'portal_actions':
                    actions.extend(provider.listActionInfos(
                                   object=object,
                                   ignore_categories=ignore_categories
                                   ))
                else:
                    actions.extend(provider.listActionInfos(object=object))

        # Include actions from object.
        if object is not None:
            if IActionProvider.providedBy(object):
                actions.extend(object.listActionInfos(object=object))

        # Reorganize the actions by category.
        filtered_actions={'user':[],
                          'folder':[],
                          'object':[],
                          'global':[],
                          'workflow':[],
                          }

        for action in actions:
            catlist = filtered_actions.setdefault(action['category'], [])
            catlist.append(action)

        return filtered_actions

InitializeClass(ActionsTool)
