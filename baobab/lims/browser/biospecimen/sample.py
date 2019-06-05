from DateTime import DateTime
from zope.schema import ValidationError

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.workflow import doActionFor
from bika.lims.browser import BrowserView
from baobab.lims import bikaMessageFactory as _
from baobab.lims.interfaces import IProject
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.utils import tmpID
from plone.registry.interfaces import IRegistry
from zope.component import queryUtility
import datetime
from baobab.lims.utils.audit_logger import AuditLogger
from baobab.lims.subscribers.utils import getLocalServerTime

class UpdateBoxes(BrowserView):
    """
    Verify the status of the box when a new biospecimen stored
    """
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.context = context
        self.request = request

    def __call__(self):
        if 'locTitle' in self.request.form:
            location_title = self.request.form['locTitle']
            if location_title:
                bsc = getToolByName(self.context, "portal_catalog")
                brains = bsc.searchResults(portal_type='StoragePos', title=location_title)
                location = brains[0].getObject()
                state = self.context.portal_workflow.getInfoFor(location, 'review_state')
                if state != 'occupied':
                    doActionFor(location, 'occupy')
                    self.context.update_box_status(location)

                prev_location = self.context.getStorageLocation()
                if prev_location and prev_location != location:
                    state = self.context.portal_workflow.getInfoFor(prev_location, 'review_state')
                    if state == 'occupied':
                        doActionFor(prev_location, 'liberate')
                        self.context.update_box_status(prev_location)
            else:
                location = self.context.getStorageLocation()
                if location:
                    doActionFor(location, 'liberate')
                    self.context.update_box_status(location)

        return []


class SampleView(BrowserView):
    """The view of a single sample
    """
    template = ViewPageTemplateFile("templates/sample_view.pt")
    title = _("Biospecimen View")

    def __call__(self):
        context = self.context
        self.absolute_url = context.absolute_url()

        # __Disable the add new menu item__ #
        context.setLocallyAllowedTypes(())

        # __Collect general data__ #
        self.id = context.getId()
        self.title = context.Title()
        self.icon = self.portal_url + "/++resource++baobab.lims.images/" \
                                    + "biospecimen_big.png"
        parent = context.getField('LinkedSample').get(context)
        self.parent_aliquot = parent and "<a href='%s'>%s</a>" % (
                                     parent.absolute_url(),
                                     parent.Title()) or None

        self.project = "<a href='%s'>%s</a>" % (
            context.aq_parent.absolute_url(),
            context.aq_parent.Title()
        )

        kit = context.getField('Kit').get(context)
        self.kit = kit and "<a href='%s'>%s</a>" % (
                       kit.absolute_url(),
                       kit.Title()) or None

        sample_batch = context.getField('Batch').get(context)
        self.sample_batch = sample_batch and "<a href='%s'>%s</a>" % (
                                 sample_batch.absolute_url(),
                                 sample_batch.Title()) or None

        self.sample_type = context.getSampleType() and context.getSampleType().Title() or ''

        location = context.getField('StorageLocation').get(context)
        self.location = location and "<a href='%s'>%s</a>" % (
                                 location.absolute_url(),
                                 location.Title()) or None

        self.sampling_date = context.getSamplingDate()

        # self.frozen_time = context.getFrozenTime()
        self.frozen_time = context.getField('FrozenTime').get(context)

        self.subjectID = context.getField('SubjectID').get(context)
        self.barcode = context.getField('Barcode').get(context)
        self.volume = context.getField('Volume').get(context) + " " + context.getField('Unit').get(context)
        self.babyNumber = context.getField('BabyNumber').get(context)
        if self.babyNumber == '0':
            self.babyNumber = None

        return self.template()


class EditView(BrowserView):
    template = ViewPageTemplateFile('templates/sample_edit.pt')

    def __call__(self):
        request = self.request
        context = self.context
        self.form = request.form

        if 'submitted' in request:
            # audit_folder = self.context.auditlogs
            audit_logger = AuditLogger(self.context, 'Sample')


            try:
                self.validate_form_input()
            except ValidationError as e:
                self.form_error(e.message)
                return

            member = audit_logger.get_member()

            pc = getToolByName(context, "portal_catalog")
            parent = context.aq_parent

            if IProject.providedBy(parent):
                folder = parent
            else:
                folder = pc(portal_type="Project", UID=request.form['Project_uid'])[0].getObject()

            new_sample = False
            if not folder.hasObject(context.getId()):
                sample = _createObjectByType('Sample', folder, tmpID())
                new_sample = True
            else:
                sample = context
                self.perform_sample_audit(sample, request)

            if IProject.providedBy(parent):
                sample.getField('Project').set(sample, parent)
            else:
                sample.getField('Project').set(sample, request.form['Project_uid'])


            # sample.getField('AllowSharing').set(sample, request.form['AllowSharing'])
            sample.getField('Kit').set(sample, request.form['Kit_uid'])
            sample.getField('StorageLocation').set(sample, request.form['StorageLocation_uid'])
            sample.getField('SubjectID').set(sample, request.form['SubjectID'])
            sample.getField('Barcode').set(sample, request.form['Barcode'])
            sample.getField('Volume').set(sample, request.form['Volume'])

            if request.form.has_key('customUnit'):
                request.form['Unit'] = request.form['customUnit']
            sample.getField('Unit').set(sample, request.form['Unit'])

            sample.getField('LinkedSample').set(sample, request.form['LinkedSample_uid'])

            sample.getField('ChangeUserName').set(sample, member)
            sample.getField('ChangeDateTime').set(sample, DateTime())

            if not sample.getField('DateCreated').get(sample):
                sample.getField('DateCreated').set(sample, DateTime())
            sample.edit(
                SampleType=request.form['SampleType_uid']
            )
            sample_batch = sample.getField('Batch').get(sample)
            sample.processForm()

            #units = []
            #registry = queryUtility(IRegistry)
            #if registry is not None:
            #    for unit in registry.get('baobab.lims.biospecimen.units', ()):
            #        units.append(unit)
            #    units.append(unicode(request.form['Unit']))
            #unit_tuple = tuple(units)

            #registry.records.get('baobab.lims.biospecimen.units')._set_value(unit_tuple)

            sample.getField('Batch').set(sample, sample_batch)
            obj_url = sample.absolute_url_path()

            if new_sample:
                audit_logger.perform_simple_audit(sample, 'New')

            request.response.redirect(obj_url)
            return

        return self.template()

    def perform_sample_audit(self, sample, request):
        audit_logger = AuditLogger(self.context, 'Sample')
        bc = getToolByName(self.context, 'bika_catalog')
        pc = getToolByName(self.context, "portal_catalog")

        # sample_audit = {}

        audit_logger.perform_reference_audit(sample, 'Kit', sample.getField('Kit').get(sample),
                                             bc, request.form['Kit_uid'])
        audit_logger.perform_reference_audit(sample, 'StorageLocation', sample.getField('StorageLocation').get(sample),
                                             pc, request.form['StorageLocation_uid'])

        sampling_date = request.form['SamplingDate']
        if sampling_date:
            sampling_date = DateTime(getLocalServerTime(sampling_date))
        else:
            sampling_date = None
        if sample.getField('SamplingDate').get(sample) != sampling_date:
            audit_logger.perform_simple_audit(sample, 'SamplingDate', sample.getField('SamplingDate').get(sample),
                                              sampling_date)

        if sample.getField('SubjectID').get(sample) != request.form['SubjectID']:
            audit_logger.perform_simple_audit(sample, 'SubjectID', sample.getField('SubjectID').get(sample),
                                              request.form['SubjectID'])
        if sample.getField('Volume').get(sample) != request.form['Volume']:
            audit_logger.perform_simple_audit(sample, 'Volume', sample.getField('Volume').get(sample), request.form['Volume'])

        if sample.getField('Barcode').get(sample) != request.form['Barcode']:
            audit_logger.perform_simple_audit(sample, 'Barcode', sample.getField('Barcode').get(sample),
                                              request.form['Barcode'])

        if sample.getField('Unit').get(sample) != request.form['Unit']:
            audit_logger.perform_simple_audit(sample, 'Unit', sample.getField('Unit').get(sample), request.form['Unit'])

        audit_logger.perform_reference_audit(sample, 'LinkedSample', sample.getField('LinkedSample').get(sample),
                                             pc, request.form['LinkedSample_uid'])

        if not sample.getField('DateCreated').get(sample):
            audit_logger.perform_simple_audit(sample, 'DateCreated', sample.getField('DateCreated').get(sample), str(DateTime()))

        audit_logger.perform_reference_audit(sample, 'SampleType', sample.getField('SampleType').get(sample),
                                             pc, request.form['SampleType_uid'])

        frozen_time = request.form['FrozenTime']
        if frozen_time:
            frozen_time = DateTime(getLocalServerTime(frozen_time))
        else:
            frozen_time = None
        if sample.getField('FrozenTime').get(sample) != frozen_time:
            audit_logger.perform_simple_audit(sample, 'FrozenTime', sample.getField('FrozenTime').get(sample), frozen_time)

        if sample.getField('BabyNumber').get(sample) != request.form['BabyNumber']:
            audit_logger.perform_simple_audit(sample, 'BabyNumber', sample.getField('BabyNumber').get(sample), request.form['BabyNumber'])

    # def get_member(self):
    #     membership = getToolByName(self.context, 'portal_membership')
    #     if membership.isAnonymousUser():
    #         member = 'anonymous'
    #     else:
    #         member = membership.getAuthenticatedMember().getUserName()
    #
    #     return member
    #
    # def perform_simple_audit(self, changed_item, changed_field='New', old_value=None, new_value=None):
    #     audit_folder = self.context.auditlogs
    #
    #     audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
    #     audit_object.edit(
    #         title='%s_%s' % (DateTime(), self.get_member()),
    #         AuditDate=DateTime(),
    #         AuditUser=self.get_member(),
    #         ItemType='Sample',
    #         ItemTitle=changed_item.Title(),
    #         ItemUID=changed_item.UID(),
    #         ChangedValue=changed_field,
    #         OldValue=old_value,
    #         NewValue=new_value,
    #     )
    #     audit_object.reindexObject()
    #
    # def perform_reference_audit(self, changed_item, changed_field, old_reference, catalog, new_uid):
    #     audit_folder = self.context.auditlogs
    #
    #     new_title = ''
    #     old_title = ''
    #
    #     if new_uid:
    #         new_items_list = catalog(UID=new_uid)
    #
    #         if new_items_list:
    #             new_item = new_items_list[0].getObject()
    #             new_title = new_item.Title()
    #
    #     if old_reference:
    #         old_title = old_reference.Title()
    #
    #     if old_title != new_title:
    #
    #         audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
    #         audit_object.edit(
    #             title='%s_%s' % (DateTime(), self.get_member()),
    #             AuditDate=DateTime(),
    #             AuditUser=self.get_member(),
    #             ItemType='Sample',
    #             ItemTitle=changed_item.Title(),
    #             ItemUID=changed_item.UID(),
    #             ChangedValue=changed_field,
    #             OldValue=old_reference.Title(),
    #             NewValue=new_title,
    #         )
    #         audit_object.reindexObject()

    def validate_form_input(self):
        subject_id = self.form.get('SubjectID')
        if not subject_id:
            raise ValidationError(['Subject ID cannot be empty!'])
        sampling_date = self.form.get('SamplingDate')
        if not sampling_date:
            raise ValidationError(['Sampling Date cannot be empty!'])

    def form_error(self, msg):
        self.context.plone_utils.addPortalMessage(msg)
        self.request.response.redirect(self.context.absolute_url())

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
