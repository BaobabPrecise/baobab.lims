from Products.CMFCore.utils import getToolByName

from bika.lims.idserver import generateUniqueId as generate

import transaction


def generateUniqueId(context, edit=False):
    """Id generation specific to Baoabab lims (overriding Bika lims)
    """
    if context.portal_type == "Sample":
        barcode = context.getField('Barcode')
        barcode_value = barcode.get(context)
        if barcode_value:
            return barcode_value
        else:
            return generate(context)

    elif context.portal_type == "SampleBatch":

        if context.getBatchId():
            id = context.getBatchId()
        else:
            subject_id = context.getSubjectID()
            date_created = context.getDateCreated().strftime('%g%m%d')

            if edit and not isSubjectOrDateModified(context, subject_id, date_created):
                return None

            bc = getToolByName(context, 'bika_catalog')
            brains = bc(portal_type="SampleBatch", getSubjectID=subject_id)
            suffix = '1'
            prefix = subject_id + '-' + date_created
            suffixes = [int(brain.id.split('-')[-1])
                        for brain in brains if brain.id.startswith(prefix)]
            if suffixes:
                suffix = str(max(suffixes) + 1)

            id = prefix + '-' + suffix
            context.title = prefix + '-' + suffix

        return id

    # Analysis Request IDs
    elif context.portal_type == "AnalysisRequest":
        return generate(context)
    else:
        return generate(context)


def isSubjectOrDateModified(context, subject_id, date_created):
    try:
        old_subject_id = context.Title()[:len(subject_id)]

        old_date_start = len(subject_id) + 1
        old_date_end = old_date_start + len(date_created)
        old_date_created = context.Title()[old_date_start:old_date_end]

        if subject_id != old_subject_id or date_created != old_date_created:
            return True
        return False

    except:
        return True


def renameAfterCreation(obj):
    transaction.savepoint(optimistic=True)
    new_id = generateUniqueId(obj)
    obj.aq_inner.aq_parent.manage_renameObject(obj.id, new_id)
    return new_id


def renameAfterEdit(obj):
    transaction.savepoint(optimistic=True)

    new_id = generateUniqueId(obj, True)
    if new_id:
        if new_id != obj.id:
            obj.aq_inner.aq_parent.manage_renameObject(obj.id, new_id)
    return new_id
