from DateTime import DateTime

from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName

from bika.lims.utils import tmpID


class AuditLogger(object):

    def __init__(self, context):
        self.context = context

    def get_member(self):
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            member = 'anonymous'
        else:
            member = membership.getAuthenticatedMember().getUserName()

        return member

    def perform_simple_audit(self, changed_item=None, changed_field='New', old_value=None, new_value=None):
        audit_folder = self.context.auditlogs

        audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
        item_title = 'Sample Import'
        if changed_item:
            item_title = changed_item.Title()

        item_uid = 'N/A'
        if changed_item:
            item_uid = changed_item.UID()

        audit_object.edit(
            title='%s_%s' % (DateTime(), self.get_member()),
            AuditDate=DateTime(),
            AuditUser=self.get_member(),
            ItemType='Sample',
            ItemTitle=item_title,
            ItemUID=item_uid,
            ChangedValue=changed_field,
            OldValue=old_value,
            NewValue=new_value,
        )
        audit_object.reindexObject()

    def perform_reference_audit(self, changed_item, changed_field, old_reference, catalog, new_uid):
        audit_folder = self.context.auditlogs

        new_title = ''
        old_title = ''

        if new_uid:
            new_items_list = catalog(UID=new_uid)

            if new_items_list:
                new_item = new_items_list[0].getObject()
                new_title = new_item.Title()

        if old_reference:
            old_title = old_reference.Title()

        if old_title != new_title:

            audit_object = _createObjectByType('AuditLog', audit_folder, tmpID())
            audit_object.edit(
                title='%s_%s' % (DateTime(), self.get_member()),
                AuditDate=DateTime(),
                AuditUser=self.get_member(),
                ItemType='Sample',
                ItemTitle=changed_item.Title(),
                ItemUID=changed_item.UID(),
                ChangedValue=changed_field,
                OldValue=old_reference.Title(),
                NewValue=new_title,
            )
            audit_object.reindexObject()
