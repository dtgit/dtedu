##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Browser views for folders.

$Id: folder.py 77366 2007-07-03 16:14:33Z yuppie $
"""

from DocumentTemplate import sequence
from Products.PythonScripts.standard import thousands_commas
from ZTUtils import Batch
from ZTUtils import LazyFilter
from ZTUtils import make_query

from Products.CMFCore.interfaces import IDynamicType
from Products.CMFDefault.exceptions import CopyError
from Products.CMFDefault.exceptions import zExceptions_Unauthorized
from Products.CMFDefault.permissions import AddPortalContent
from Products.CMFDefault.permissions import DeleteObjects
from Products.CMFDefault.permissions import ListFolderContents
from Products.CMFDefault.permissions import ManageProperties
from Products.CMFDefault.permissions import ViewManagementScreens
from Products.CMFDefault.utils import html_marshal
from Products.CMFDefault.utils import translate
from Products.CMFDefault.utils import Message as _

from utils import decode
from utils import memoize
from utils import ViewBase


# XXX: This should be refactored using formlib. Please don't import from this
#      module, things might be changed without further notice.

class FormViewBase(ViewBase):

    # helpers

    def _setRedirect(self, provider_id, action_path, keys=''):
        provider = self._getTool(provider_id)
        try:
            target = provider.getActionInfo(action_path, self.context)['url']
        except ValueError:
            target = self._getPortalURL()

        kw = {}
        message = self.request.other.get('portal_status_message', '')
        if message:
            if isinstance(message, unicode):
                message = message.encode(self._getBrowserCharset())
            kw['portal_status_message'] = message
        for k in keys.split(','):
            k = k.strip()
            v = self.request.form.get(k, None)
            if v:
                kw[k] = v

        query = kw and ( '?%s' % make_query(kw) ) or ''
        self.request.RESPONSE.redirect( '%s%s' % (target, query) )

        return True

    # interface

    def __call__(self, **kw):
        form = self.request.form
        for button in self._BUTTONS:
            if button['id'] in form:
                for permission in button.get('permissions', ()):
                    if not self._checkPermission(permission):
                        break
                else:
                    for transform in button.get('transform', ()):
                        status = getattr(self, transform)(**form)
                        if isinstance(status, bool):
                            status = (status,)
                        if len(status) > 1:
                            message = translate(status[1], self.context)
                            self.request.other['portal_status_message'] = message
                        if not status[0]:
                            return self.index()
                    if self._setRedirect(*button['redirect']):
                        return
        return self.index()

    @memoize
    def form_action(self):
        return self._getViewURL()

    @memoize
    def listButtonInfos(self):
        form = self.request.form
        buttons = []
        for button in self._BUTTONS:
            if button.get('title', None):
                for permission in button.get('permissions', ()):
                    if not self._checkPermission(permission):
                        break
                else:
                    for condition in button.get('conditions', ()):
                        if not getattr(self, condition)():
                            break
                    else:
                        buttons.append({'name': button['id'],
                                        'value': button['title']})
        return tuple(buttons)

    @memoize
    @decode
    def listHiddenVarInfos(self):
        kw = self._getHiddenVars()
        vars = [ {'name': name, 'value': value}
                 for name, value in html_marshal(**kw) ]
        return tuple(vars)


class BatchViewBase(ViewBase):

    # helpers

    _BATCH_SIZE = 25

    @memoize
    def _getBatchStart(self):
        return self.request.form.get('b_start', 0)

    @memoize
    def _getBatchObj(self):
        b_start = self._getBatchStart()
        items = self._getItems()
        return Batch(items, self._BATCH_SIZE, b_start, orphan=0)

    @memoize
    def _getHiddenVars(self):
        return {}

    @memoize
    def _getNavigationVars(self):
        return self._getHiddenVars()

    @memoize
    def _getNavigationURL(self, b_start):
        target = self._getViewURL()
        kw = self._getNavigationVars().copy()

        kw['b_start'] = b_start
        for k, v in kw.items():
            if not v or k == 'portal_status_message':
                del kw[k]

        query = kw and ('?%s' % make_query(kw)) or ''
        return u'%s%s' % (target, query)

    # interface

    @memoize
    @decode
    def listItemInfos(self):
        batch_obj = self._getBatchObj()
        portal_url = self._getPortalURL()

        items = []
        for item in batch_obj:
            item_description = item.Description()
            item_icon = item.getIcon(1)
            item_title = item.Title()
            item_type = remote_type = item.Type()
            if item_type == 'Favorite' and not item_icon == 'p_/broken':
                item = item.getObject()
                item_description = item_description or item.Description()
                item_title = item_title or item.Title()
                remote_type = item.Type()
            is_file = remote_type in ('File', 'Image')
            is_link = remote_type == 'Link'
            items.append({'description': item_description,
                          'format': is_file and item.Format() or '',
                          'icon': item_icon and ('%s/%s' %
                                               (portal_url, item_icon)) or '',
                          'size': is_file and ('%0.0f kb' %
                                            (item.get_size() / 1024.0)) or '',
                          'title': item_title,
                          'type': item_type,
                          'url': is_link and item.getRemoteUrl() or
                                 item.absolute_url()})
        return tuple(items)

    @memoize
    def navigation_previous(self):
        batch_obj = self._getBatchObj().previous
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Previous item')
        else:
            title = _(u'Previous ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    @memoize
    def navigation_next(self):
        batch_obj = self._getBatchObj().next
        if batch_obj is None:
            return None

        length = len(batch_obj)
        url = self._getNavigationURL(batch_obj.first)
        if length == 1:
            title = _(u'Next item')
        else:
            title = _(u'Next ${count} items', mapping={'count': length})
        return {'title': title, 'url': url}

    @memoize
    def summary_length(self):
        length = self._getBatchObj().sequence_length
        return length and thousands_commas(length) or ''

    @memoize
    def summary_type(self):
        length = self._getBatchObj().sequence_length
        return (length == 1) and _(u'item') or _(u'items')

    @memoize
    @decode
    def summary_match(self):
        return self.request.form.get('SearchableText')


class FolderView(BatchViewBase):

    """View for IFolderish.
    """

    # helpers

    @memoize
    def _getItems(self):
        (key, reverse) = self.context.getDefaultSorting()
        items = self.context.contentValues()
        items = sequence.sort(items,
                              ((key, 'cmp', reverse and 'desc' or 'asc'),))
        return LazyFilter(items, skip='View')

    # interface

    @memoize
    def has_local(self):
        return 'local_pt' in self.context.objectIds()


class FolderContentsView(BatchViewBase, FormViewBase):

    """Contents view for IFolderish.
    """

    _BUTTONS = ({'id': 'items_new',
                 'title': _(u'New...'),
                 'permissions': (ViewManagementScreens, AddPortalContent),
                 'conditions': ('checkAllowedContentTypes',),
                 'redirect': ('portal_types', 'object/new')},
                {'id': 'items_rename',
                 'title': _(u'Rename...'),
                 'permissions': (ViewManagementScreens, AddPortalContent),
                 'conditions': ('checkItems', 'checkAllowedContentTypes'),
                 'transform': ('validateItemIds',),
                 'redirect': ('portal_types', 'object/rename_items',
                              'b_start, ids, key, reverse')},
                {'id': 'items_cut',
                 'title': _(u'Cut'),
                 'permissions': (ViewManagementScreens,),
                 'conditions': ('checkItems',),
                 'transform': ('validateItemIds', 'cut_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_copy',
                 'title': _(u'Copy'),
                 'permissions': (ViewManagementScreens,),
                 'conditions': ('checkItems',),
                 'transform': ('validateItemIds', 'copy_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_paste',
                 'title': _(u'Paste'),
                 'permissions': (ViewManagementScreens, AddPortalContent),
                 'conditions': ('checkClipboardData',),
                 'transform': ('validateClipboardData', 'paste_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_delete',
                 'title': _(u'Delete'),
                 'permissions': (ViewManagementScreens, DeleteObjects),
                 'conditions': ('checkItems',),
                 'transform': ('validateItemIds', 'delete_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_sort',
                 'permissions': (ManageProperties,),
                 'transform': ('sort_control',),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start')},
                {'id': 'items_up',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'up_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_down',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'down_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_top',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'top_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'items_bottom',
                 'permissions': (ManageProperties,),
                 'transform': ('validateItemIds', 'bottom_control'),
                 'redirect': ('portal_types', 'object/folderContents',
                              'b_start, key, reverse')},
                {'id': 'set_view_filter',
                 'transform': ('set_filter_control',),
                 'redirect': ('portal_types', 'object/folderContents')},
                {'id': 'clear_view_filter',
                 'transform': ('clear_filter_control',),
                 'redirect': ('portal_types', 'object/folderContents')})

    # helpers

    @memoize
    def _getSorting(self):
        key = self.request.form.get('key', None)
        if key:
            return (key, self.request.form.get('reverse', 0))
        else:
            return self.context.getDefaultSorting()

    @memoize
    def _isDefaultSorting(self):
        return self._getSorting() == self.context.getDefaultSorting()

    @memoize
    def _getHiddenVars(self):
        b_start = self._getBatchStart()
        is_default = self._isDefaultSorting()
        (key, reverse) = is_default and ('', 0) or self._getSorting()
        return {'b_start': b_start, 'key': key, 'reverse': reverse}

    @memoize
    def _getItems(self):
        (key, reverse) = self._getSorting()
        folderfilter = self.request.get('folderfilter', '')
        filter = self.context.decodeFolderFilter(folderfilter)
        items = self.context.listFolderContents(contentFilter=filter)
        return sequence.sort(items,
                             ((key, 'cmp', reverse and 'desc' or 'asc'),))

    # interface

    @memoize
    @decode
    def up_info(self):
        up_obj = self.context.aq_inner.aq_parent
        mtool = self._getTool('portal_membership')
        allowed = mtool.checkPermission(ListFolderContents, up_obj)
        if allowed:
            if IDynamicType.providedBy(up_obj):
                up_url = up_obj.getActionInfo('object/folderContents')['url']
                return {'icon': '%s/UpFolder_icon.gif' % self._getPortalURL(),
                        'id': up_obj.getId(),
                        'url': up_url}
            else:
                return {'icon': '',
                        'id': 'Root',
                        'url': ''}
        else:
            return {}

    @memoize
    def listColumnInfos(self):
        (key, reverse) = self._getSorting()
        columns = ( {'key': 'Type',
                     'title': _(u'Type'),
                     'width': '20',
                     'colspan': '2'}
                  , {'key': 'getId',
                     'title': _(u'Name'),
                     'width': '360',
                     'colspan': None}
                  , {'key': 'modified',
                     'title': _(u'Last Modified'),
                     'width': '180',
                     'colspan': None}
                  , {'key': 'position',
                     'title': _(u'Position'),
                     'width': '80',
                     'colspan': None }
                  )
        for column in columns:
            if key == column['key'] and not reverse and key != 'position':
                query = make_query(key=column['key'], reverse=1)
            else:
                query = make_query(key=column['key'])
            column['url'] = '%s?%s' % (self._getViewURL(), query)
        return tuple(columns)

    @memoize
    @decode
    def listItemInfos(self):
        b_start = self._getBatchStart()
        (key, reverse) = self._getSorting()
        batch_obj = self._getBatchObj()
        items_manage_allowed = self._checkPermission(ViewManagementScreens)
        portal_url = self._getPortalURL()

        items = []
        i = 1
        for item in batch_obj:
            item_icon = item.getIcon(1)
            item_id = item.getId()
            item_position = (key == 'position') and str(b_start + i) or '...'
            i += 1
            item_url = item.getActionInfo(('object/folderContents',
                                           'object/view'))['url']
            items.append({'checkbox': items_manage_allowed and ('cb_%s' %
                                                               item_id) or '',
                          'icon': item_icon and ('%s/%s' %
                                               (portal_url, item_icon)) or '',
                          'id': item_id,
                          'modified': item.ModificationDate(),
                          'position': item_position,
                          'title': item.Title(),
                          'type': item.Type() or None,
                          'url': item_url})
        return tuple(items)

    @memoize
    def listDeltas(self):
        length = self._getBatchObj().sequence_length
        deltas = range(1, min(5, length)) + range(5, length, 5)
        return tuple(deltas)

    @memoize
    def is_orderable(self):
        length = len(self._getBatchObj())
        items_move_allowed = self._checkPermission(ManageProperties)
        (key, reverse) = self._getSorting()
        return items_move_allowed and (key == 'position') and length > 1

    @memoize
    def is_sortable(self):
        items_move_allowed = self._checkPermission(ManageProperties)
        return items_move_allowed and not self._isDefaultSorting()

    # checkers

    def checkAllowedContentTypes(self):
        return bool(self.context.allowedContentTypes())

    def checkClipboardData(self):
        return bool(self.context.cb_dataValid())

    def checkItems(self):
        return bool(self._getItems())

    # validators

    def validateItemIds(self, ids=(), **kw):
        if ids:
            return True
        else:
            return False, _(u'Please select one or more items first.')

    def validateClipboardData(self, **kw):
        if self.context.cb_dataValid():
            return True
        else:
            return False, _(u'Please copy or cut one or more items to paste '
                            u'first.')

    # controllers

    def cut_control(self, ids, **kw):
        """Cut objects from a folder and copy to the clipboard.
        """
        try:
            self.context.manage_cutObjects(ids, self.request)
            if len(ids) == 1:
                return True, _(u'Item cut.')
            else:
                return True, _(u'Items cut.')
        except CopyError:
            return False, _(u'CopyError: Cut failed.')
        except zExceptions_Unauthorized:
            return False, _(u'Unauthorized: Cut failed.')

    def copy_control(self, ids, **kw):
        """Copy objects from a folder to the clipboard.
        """
        try:
            self.context.manage_copyObjects(ids, self.request)
            if len(ids) == 1:
                return True, _(u'Item copied.')
            else:
                return True, _(u'Items copied.')
        except CopyError:
            return False, _(u'CopyError: Copy failed.')

    def paste_control(self, **kw):
        """Paste objects to a folder from the clipboard.
        """
        try:
            result = self.context.manage_pasteObjects(self.request['__cp'])
            if len(result) == 1:
                return True, _(u'Item pasted.')
            else:
                return True, _(u'Items pasted.')
        except CopyError:
            return False, _(u'CopyError: Paste failed.')
        except zExceptions_Unauthorized:
            return False, _(u'Unauthorized: Paste failed.')

    def delete_control(self, ids, **kw):
        """Delete objects from a folder.
        """
        self.context.manage_delObjects(list(ids))
        if len(ids) == 1:
            return True, _(u'Item deleted.')
        else:
            return True, _(u'Items deleted.')

    def sort_control(self, key='position', reverse=0, **kw):
        """Sort objects in a folder.
        """
        self.context.setDefaultSorting(key, reverse)
        return True

    def up_control(self, ids, delta, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsUp(ids, delta,
                                                 subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved up.')
            elif attempt > 1:
                return True, _(u'Items moved up.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')

    def down_control(self, ids, delta, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsDown(ids, delta,
                                                   subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved down.')
            elif attempt > 1:
                return True, _(u'Items moved down.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')

    def top_control(self, ids, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsToTop(ids,
                                                    subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved to top.')
            elif attempt > 1:
                return True, _(u'Items moved to top.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')

    def bottom_control(self, ids, **kw):
        subset_ids = [ obj.getId()
                       for obj in self.context.listFolderContents() ]
        try:
            attempt = self.context.moveObjectsToBottom(ids,
                                                       subset_ids=subset_ids)
            if attempt == 1:
                return True, _(u'Item moved to bottom.')
            elif attempt > 1:
                return True, _(u'Items moved to bottom.')
            else:
                return False, _(u'Nothing to change.')
        except ValueError:
            return False, _(u'ValueError: Move failed.')

    def set_filter_control(self, **kw):
        filter = self.context.encodeFolderFilter(self.request)
        self.request.RESPONSE.setCookie('folderfilter', filter, path='/',
                                      expires='Wed, 19 Feb 2020 14:28:00 GMT')
        return True, _(u'Filter applied.')

    def clear_filter_control(self, **kw):
        self.request.RESPONSE.expireCookie('folderfilter', path='/')
        self.request.RESPONSE.expireCookie('show_filter_form', path='/')
        return True, _(u'Filter cleared.')
