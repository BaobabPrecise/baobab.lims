from DateTime import DateTime

from AccessControl import getSecurityManager
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.ATContentTypes.lib import constraintypes
from Products.CMFCore.permissions import AddPortalContent, ModifyPortalContent

from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements

from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.browser import BrowserView

from baobab.lims import bikaMessageFactory as _
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.subscribers.utils import getLocalServerTime


class BoxMovementsView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        BikaListingView.__init__(self, context, request)

        self.context = context
        self.catalog = 'bika_catalog'
        request.set('disable_plone.rightcolumn', 1)
        self.contentFilter = {
            'portal_type': 'BoxMovement',
        }
        self.context_actions = {_('Add'):
                                    {'url': 'createObject?type_name=BoxMovement',
                                     'icon': '++resource++bika.lims.images/add.png'}}
        self.title = self.context.translate(_("Box Movements"))
        self.icon = self.portal_url + \
                    "/++resource++baobab.lims.images/patient_big.png"
        self.description = ''
        self.show_sort_column = False
        self.show_select_row = False
        self.show_select_column = False
        self.pagesize = 25
        self.allow_edit = True

        if self.context.portal_type == 'BoxMovements':
            self.request.set('disable_border', 1)

        self.columns = {
            'Title': {
                'title': _('Title'),
                'index': 'sortable_title'
            },
            'DateCreated': {
                'title': _('Date Created'),
                'index': 'sortable_title'
            },
            'StorageLocation': {
                'title': _('From Storage'),
                'index': 'sortable_title'
            },
            'LabContact': {
                'title': _('Lab Contact'),
                'index': 'sortable_title'
            },
            'NewLocation': {
                'title': _('New Location'),
                'index': 'sortable_title'
            }
        }

        self.review_states = [
            {
                'id': 'default',
                'title': _('Active'),
                'contentFilter': {
                    'inactive_state': 'active',
                    'sort_on': 'sortable_title',
                    'sort_order': 'ascending'
                },
                'transitions': [{'id': 'deactivate'}],
                'columns': [
                    'Title',
                    'DateCreated',
                    'StorageLocation',
                    'LabContact',
                    'NewLocation'
                ]
            },
            {
                'id': 'inactive',
                'title': _('Inactive'),
                'contentFilter': {
                    'inactive_state': 'inactive',
                    'sort_on': 'sortable_title',
                    'sort_order': 'ascending'
                },
                'transitions': [{'id': 'activate'}],
                'columns': [
                    'Title',
                    'DateCreated',
                    'StorageLocation',
                    'LabContact',
                    'NewLocation'
                ]
            }
        ]

    def __call__(self):
        if getSecurityManager().checkPermission(AddPortalContent, self.context):
            self.show_select_row = True
            self.show_select_column = True

        return BikaListingView.__call__(self)

    def folderitems(self, full_objects=False):

        items = BikaListingView.folderitems(self)

        for x in range(len(items)):

            if not items[x].has_key('obj'):
                continue
            obj = items[x]['obj']

            items[x]['replace']['Title'] = "<a href='%s'>%s</a>" % \
                                           (items[x]['url'], items[x]['Title'])
            items[x]['DateCreated'] = obj.getField('DateCreated').get(obj)
            storageLocation = obj.getField('StorageLocation').get(obj)
            if storageLocation:
                items[x]['StorageLocation'] = storageLocation.Title()

            labContact = obj.getField('LabContact').get(obj)
            if labContact:
                items[x]['LabContact'] = labContact.Title()

            newLocation = obj.getField('NewLocation').get(obj)
            if newLocation:
                items[x]['NewLocation'] = newLocation.Title()

        return items

class BoxMovementView(BrowserView):
    """
    """
    template = ViewPageTemplateFile("templates/boxmovement_view.pt")
    title = _("Box Movement")

    def __call__(self):
        context = self.context
        portal = self.portal
        self.absolute_url = context.absolute_url()
        setup = portal.bika_setup

        # __Disable the add new menu item__ #
        context.setLocallyAllowedTypes(())

        # __Collect general data__ #
        self.id = context.getId()
        self.title = context.Title()
        self.date_created = context.getDateCreated()
        self.from_storage = context.getStorageLocation().title
        self.lab_contact = context.getLabContact().title
        self.new_location = context.getNewLocation().title

        return self.template()

class BoxMovementEdit(BrowserView):
    template = ViewPageTemplateFile('templates/boxmovement_edit.pt')

    def __call__(self):
        # portal = self.portal
        request = self.request
        context = self.context
        # setup = portal.bika_setup

        if 'submitted' in request:

            # pdb.set_trace()
            context.setConstrainTypesMode(constraintypes.DISABLED)
            # This following line does the same as precedent which one is the
            #  best?
            # context.aq_parent.setConstrainTypesMode(constraintypes.DISABLED)

            portal_factory = getToolByName(context, 'portal_factory')
            context = portal_factory.doCreate(context, context.id)

            self.perform_boxmovement_audit(context, request)

            context.processForm()

            obj_url = context.absolute_url_path()
            request.response.redirect(obj_url)
            return

        return self.template()

    def perform_boxmovement_audit(self, boxmovement, request):

        audit_logger = AuditLogger(self.context, 'BoxMovement')
        bc = getToolByName(self.context, 'bika_catalog')
        pc = getToolByName(self.context, "portal_catalog")

        audit_logger.perform_reference_audit(boxmovement, 'StorageLocation', boxmovement.getField('StorageLocation').get(boxmovement),
                                             pc, request.form['StorageLocation_uid'])

        date_created = request.form['DateCreated']
        if date_created:
            date_created = DateTime(getLocalServerTime(date_created))
        else:
            date_created = None
        if boxmovement.getField('DateCreated').get(boxmovement) != date_created:
            audit_logger.perform_simple_audit(boxmovement, 'DateCreated', boxmovement.getField('DateCreated').get(boxmovement), date_created)

        audit_logger.perform_reference_audit(boxmovement, 'LabContact',
                                             boxmovement.getField('LabContact').get(boxmovement),
                                             pc, request.form['LabContact_uid'])

        audit_logger.perform_reference_audit(boxmovement, 'NewLocation', boxmovement.getField('NewLocation').get(boxmovement),
                                             pc, request.form['NewLocation_uid'])

    def get_fields_with_visibility(self, visibility, mode=None):
        mode = mode if mode else 'edit'
        schema = self.context.Schema()
        fields = []
        for field in schema.fields():
            isVisible = field.widget.isVisible
            v = isVisible(self.context, mode, default='invisible', field=field)
            if v == visibility:
                fields.append(field)
        return fields