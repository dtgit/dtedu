from zope.interface import implements

from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner, aq_chain
from OFS.Image import File

from Products.CMFCore.utils import getToolByName

from Products.Archetypes.public import BaseBTreeFolderSchema, Schema, TextField
from Products.Archetypes.public import BaseBTreeFolder, registerType
from Products.Archetypes.public import TextAreaWidget
from Products.Ploneboard.config import PROJECTNAME

from Products.CMFPlone.utils import _createObjectByType

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin
from Products.Ploneboard.permissions import (
    ViewBoard, AddComment, ManageConversation, EditComment)
from Products.Ploneboard.interfaces import IForum, IConversation

from Products.Ploneboard import utils

from Products.CMFPlone.interfaces.NonStructuralFolder \
    import INonStructuralFolder as ZopeTwoINonStructuralFolder
from Products.CMFPlone.interfaces.structure import INonStructuralFolder

PBConversationBaseBTreeFolderSchema = BaseBTreeFolderSchema.copy()
PBConversationBaseBTreeFolderSchema['title'].read_permission = ViewBoard
PBConversationBaseBTreeFolderSchema['title'].write_permission = EditComment

schema = PBConversationBaseBTreeFolderSchema + Schema((
    TextField('description',
              searchable = 1,
              read_permission = ViewBoard,
              write_permission = EditComment,
              default_content_type = 'text/plain',
              default_output_type = 'text/plain',
              widget = TextAreaWidget(description = "Enter a brief description of the conversation.",
                                      description_msgid = "help_description_conversation",
                                      label = "Description",
                                      label_msgid = "label_description_conversation",
                                      i18n_domain = "ploneboard",
                                      rows = 5)),
    ))
utils.finalizeSchema(schema)


class PloneboardConversation(BrowserDefaultMixin, BaseBTreeFolder):
    """Conversation contains comments."""

    implements(IConversation, INonStructuralFolder)
    __implements__ = (BaseBTreeFolder.__implements__, BrowserDefaultMixin.__implements__, ZopeTwoINonStructuralFolder)

    meta_type = 'PloneboardConversation'

    schema = schema

    _at_rename_after_creation = True


    security = ClassSecurityInfo()

    def getCatalog(self):
        return getToolByName(self, 'portal_catalog')

    security.declareProtected(ManageConversation, 'edit')
    def edit(self, **kwargs):
        """Alias for update()
        """
        self.update(**kwargs)

    security.declareProtected(ViewBoard, 'getTitle')
    def getTitle(self):
        """Get the title of this conversation"""
        return self.Title()

    security.declareProtected(ViewBoard, 'getForum')
    def getForum(self):
        """Returns containing forum."""
        # Try containment
        stoptypes = ['Plone Site']
        for obj in aq_chain(aq_inner(self)):
            if hasattr(obj, 'portal_type') and obj.portal_type not in stoptypes:
                if IForum.providedBy(obj):
                    return obj
        return None

    security.declareProtected(ManageConversation, 'removeComment')
    def removeComment( self, comment):
        self.manage_delObjects([comment.getId()])
        # XXX reparent replies to this comment ?

    security.declareProtected(AddComment, 'addComment')
    def addComment( self, title, text, creator=None, files=None):
        """Adds a new comment with subject and body."""
        id = self.generateId(prefix='')
        if not title:
            title = self.Title()


        m = _createObjectByType('PloneboardComment', self, id)

        # XXX: There is some permission problem with AT write_permission
        # and using **kwargs in the _createObjectByType statement.
        m.setTitle(title)
        m.setText(text)
        if creator is not None:
            m.setCreators([creator])

        # Create files in message
        if files:
            for file in files:
                # Get raw filedata, not persistent object with reference to tempstorage
                attachment = File(file.getId(), file.title_or_id(), str(file.data), file.getContentType())
                m.addAttachment(attachment)

        # If this comment is being added by anonymous, make sure that the true
        # owner in zope is the owner of the forum, not the parent comment or
        # conversation. Otherwise, that owner may be able to view or delete
        # the comment.
        membership = getToolByName(self, 'portal_membership')
        if membership.isAnonymousUser():
            forum = self.getForum()
            utils.changeOwnershipOf(m, forum.owner_info()['id'], False)

        m.indexObject()

        self.reindexObject() # Sets modified
        return m

    security.declareProtected(ViewBoard, 'getComment')
    def getComment(self, comment_id, default=None):
        """Returns the comment with the specified id."""
        #return self._getOb(comment_id, default)
        comments = self.getCatalog()(
                object_provides='Products.Ploneboard.interfaces.IComment',
                getId=comment_id)
        if comments:
            return comments[0].getObject()
        else:
            return None

    security.declareProtected(ViewBoard, 'getComments')
    def getComments(self, limit=30, offset=0, **kw):
        """
        Retrieves the specified number of comments with offset 'offset'.
        In addition there are kw args for sorting and retrieval options.
        """
        query = {'object_provides' : 'Products.Ploneboard.interfaces.IComment',
                 'sort_on'           : 'created',
                 'sort_limit'        : (offset+limit),
                 'path'              : '/'.join(self.getPhysicalPath()),}
        query.update(kw)
        catalog=self.getCatalog()
        return [f.getObject() for f in catalog(**query)[offset:offset+limit]]

    security.declareProtected(ViewBoard, 'getNumberOfComments')
    def getNumberOfComments(self):
        """
        Returns the number of comments in this conversation.
        """
        return len(self.getCatalog()(
            object_provides='Products.Ploneboard.interfaces.IComment',
            path='/'.join(self.getPhysicalPath())))

    security.declareProtected(ViewBoard, 'getLastCommentDate')
    def getLastCommentDate(self):
        """
        Returns a DateTime corresponding to the timestamp of the last comment
        for the conversation.
        """
        comment = self.getLastComment()
        if comment:
            return comment.created()
        return None

    security.declareProtected(ViewBoard, 'getLastCommentAuthor')
    def getLastCommentAuthor(self):
        """
        Returns the name of the author of the last comment.
        """

        comment = self.getLastComment()
        if comment:
            return comment.Creator()
        return None

    security.declareProtected(ViewBoard, 'getLastComment')
    def getLastComment(self):
        """
        Returns the last comment as full object..
        Returns None if there is no comment
        """

        res = self.getCatalog()(
                object_provides='Products.Ploneboard.interfaces.IComment', \
                sort_on='created', sort_order='reverse', sort_limit=1,
                path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].getObject()
        return None

    security.declareProtected(ViewBoard, 'getRootComments')
    def getRootComments(self):
        """
        Return a list all comments rooted to the board; ie comments which
        are not replies to other comments.
        """
        raw = self.getComments()
        ours = [ comment for comment in raw if comment.inReplyToUID() is None]
        return ours

    security.declareProtected(ViewBoard, 'getFirstComment')
    def getFirstComment(self):
        """
        See IConversation.getFirstComment.__doc__
        """
        res = self.getCatalog()(
                object_provides='Products.Ploneboard.interfaces.IComment',
                sort_on='created', sort_limit=1,
                path='/'.join(self.getPhysicalPath()))
        if res:
            return res[0].getObject()
        else:
            return None

    security.declareProtected(ManageConversation, 'moveToForum')
    def moveToForum(self, forum_id):
        """Moves conversation to another forum"""
        forum = self.getForum().getBoard().getForum(forum_id)
        if forum:
            parent = self.getForum()
            cut_objects = parent.manage_cutObjects((self.getId(),) )
            forum.manage_pasteObjects(cut_objects)

    security.declareProtected(ManageConversation, 'delete')
    def delete(self):
        """"""
        parent = self.getForum()
        parent._delObject(self.getId())

    security.declareProtected(ViewBoard, 'Creator')
    def Creator(self):
        # XXX Backwards compatability with old version
        return getattr(self, '_creator', None) or BaseBTreeFolder.Creator(self)

    def __nonzero__(self):
        return 1

    # No setting of default page - makes no sense
    def canSetDefaultPage(self):
        return False

registerType(PloneboardConversation, PROJECTNAME)
