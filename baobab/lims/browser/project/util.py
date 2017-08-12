from Products.CMFCore.utils import getToolByName
from zope.schema import ValidationError
from Products.CMFPlone.utils import _createObjectByType
from DateTime import DateTime
from plone import api

from bika.lims.workflow import doActionFor
from bika.lims.utils import tmpID

from baobab.lims.interfaces import IManagedStorage

class SampleGeneration:

    def __init__(self, form, project):
        self.form = form
        self.project = project

    def create_sample(self, kit, temporary_sample_type):
        """Create sample as biospecimen or aliquot
            """
        # sample = _createObjectByType('Sample', self.project, tmpID())
        sample = api.content.create(
            container=self.project,
            type="Sample",
            id='tempID',
            SampleType= temporary_sample_type,
        )
        field = sample.getField('DateCreated')
        field.set(sample, DateTime())
        if kit:
            field_k = sample.getField('Kit')
            field_k.set(sample, kit.UID())
            field_p = sample.getField('Project')
            field_p.set(sample, self.project)


        # Return the newly created sample
        return sample

    def store_samples(self, items, storages):
        """ store items inside selected storages
        """
        wf = getToolByName(self.project, 'portal_workflow')
        for storage in storages:
            if IManagedStorage.providedBy(storage):
                free_positions = storage.get_free_positions()
                if len(items) <= len(free_positions):
                    for i, item in enumerate(items):
                        item.setStorageLocation(free_positions[i])
                        wf.doActionFor(free_positions[i], 'reserve')
                else:
                    for i, position in enumerate(free_positions):
                        items[i].setStorageLocation(position)
                        wf.doActionFor(position, 'reserve')

    def get_biospecimen_storages(self):
        """Take a list of UIDs from the form, and resolve to a list of Storages.
        Accepts ManagedStorage, UnmanagedStorage, or StoragePosition UIDs.
        """
        uc = getToolByName(self.project, 'uid_catalog')
        bio_storages = []
        form_uids = self.form['biospecimen-storage-uids'].split(',')
        for uid in form_uids:
            brain = uc(UID=uid)[0]
            instance = brain.getObject()
            if len(instance.get_free_positions()) > 0:
                bio_storages.append(instance)

        return bio_storages

    @staticmethod
    def count_storage_positions(storages):
        """"Return the number of items that can be stored in storages.
        This method is called in case all the storages are of type Managed.
        """
        count = 0
        for storage in storages:
            # If storage is a ManagedStorage, increment count for each
            # available StoragePosition
            if IManagedStorage.providedBy(storage):
                count += storage.getFreePositions()
            else:
                raise ValidationError("Storage %s is not a valid storage type" %
                                      storage)
        return count