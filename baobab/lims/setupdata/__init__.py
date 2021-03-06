from datetime import datetime

from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.exportimport.setupdata import WorksheetImporter
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.interfaces import ISetupDataSetList
from zope.interface import implements
from zope.interface import alsoProvides
from baobab.lims.idserver import renameAfterCreation
from baobab.lims.interfaces import ISampleStorageLocation, IStockItemStorage
from baobab.lims.browser.project import *
from bika.lims import logger


def get_project_multi_items(context, string_elements, portal_type, portal_catalog):

    if not string_elements:
        return []

    pc = getToolByName(context, portal_catalog)

    items = []
    file_items = [x.strip() for x in string_elements.split(';')]

    for file_item in file_items:
        item_list = pc(portal_type=portal_type, Title=file_item)
        if item_list:
            items.append(item_list[0].getObject().UID())

    return items

class ExcelSheetError(Exception):
    pass

class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname="baobab.lims")

class BaobabWorksheetImporter(WorksheetImporter):

    """Use this as a base, for normal tabular data sheet imports.
    """

    def __call__(self, lsd, workbook, dataset_project, dataset_name):
        self.lsd = lsd
        self.context = lsd.context
        self.workbook = workbook
        self.sheetname = self.__class__.__name__.replace("_", " ")
        if self.sheetname not in workbook.sheetnames:
            logger.error("Sheet '{0}' not found".format(self.sheetname))
            return
        self.worksheet = workbook.get_sheet_by_name(self.sheetname)
        self.dataset_project = dataset_project
        self.dataset_name = dataset_name
        if self.worksheet:
            logger.info("Loading {0}.{1}: {2}".format(
                self.dataset_project, self.dataset_name, self.sheetname))
            try:
                self.Import()
                for error in self._errors:
                    self.context.plone_utils.addPortalMessage(str(error), 'error')

            except IOError:
                # The importer must omit the files not found inside the server filesystem (bika/lims/setupdata/test/
                # if the file is loaded from 'select existing file' or bika/lims/setupdata/uploaded if it's loaded from
                # 'Load from file') and finishes the import without errors. https://jira.bikalabs.com/browse/LIMS-1624
                warning = "Error while loading attached file from %s. The file will not be uploaded into the system."
                logger.warning(warning, self.sheetname)
                # self.context.plone_utils.addPortalMessage("Error while loading some attached files. "
                #                                           "The files weren't uploaded into the system.")
                # self.context.plone_utils.addPortalMessage("Another deliberate test.")
                # self.context.plone_utils.addPortalMessage("Third deliberate test.")
        else:
            logger.info("No records found: '{0}'".format(self.sheetname))

    def get_member(self):
        membership = getToolByName(self.context, 'portal_membership')
        if membership.isAnonymousUser():
            member = 'anonymous'
        else:
            member = membership.getAuthenticatedMember().getUserName()

        return member


class Products(WorksheetImporter):
    """ Import test products
    """
    def Import(self):
        folder = self.context.bika_setup.bika_products
        rows = self.get_rows(3)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        suppliers = [o.getObject() for o in bsc(portal_type="Supplier")]
        for row in rows:
            title = row.get('Title')
            description = row.get('description', '')
            obj = _createObjectByType('Product', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                Hazardous=self.to_bool(row.get('Hazardous', '')),
                Quantity=self.to_int(row.get('Quantity', 0)),
                Unit=row.get('Unit', ''),
                Price=str(row.get('Price', '0.00'))
            )

            for supplier in suppliers:
                if supplier.Title() == row.get('Suppliers', ''):
                    obj.setSupplier(supplier)
                    break

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Kit_Components(WorksheetImporter):
    """ This class is called from Kit_Templates and not from LoadSetupData class
    """
    def __init__(self, lsd, workbook, dataset_project, dataset_name, template_name, catalog):
        self.lsd = lsd
        self.workbook = workbook
        self.dataset_project = dataset_project
        self.dataset_name = dataset_name
        self.template_name = template_name
        self.catalog = catalog
        self.product_list = []

        WorksheetImporter.__call__(self, self.lsd, self.workbook, self.dataset_project, self.dataset_name)

    def Import(self):
        rows = self.get_rows(3)
        product_obj = None
        for row in rows:
            if self.template_name == row.get('templateName'):
                product_name = row.get('componentName')

                brains = self.catalog.searchResults({'portal_type': 'Product', 'title': product_name})
                if brains and len(brains) == 1:
                    product_obj = brains[0].getObject()
                    self.product_list.append({
                        'product': product_name,
                        'product_uid': product_obj.UID(),
                        'value': '',
                        'quantity': row.get('quantity')
                    })

    def get_product_list(self):
        """ This method is called after Import to get computed product_list
        """
        return self.product_list


class Kit_Templates(WorksheetImporter):
    """ Kit_Templates worksheet contains only Kit Template without components. Components are listed in another
        worksheet (see Kit_Components class).
    """
    def Import(self):
        folder = self.context.bika_setup.bika_kittemplates
        rows = self.get_rows(3)
        catalog = getToolByName(self.context, 'bika_setup_catalog')
        for row in rows:
            template_name = row.get('templateName')
            kit_component = Kit_Components(self, self.workbook, self.dataset_project, self.dataset_name, template_name, catalog)
            product_list = kit_component.get_product_list()
            obj = _createObjectByType('KitTemplate', folder, tmpID())
            obj.edit(
                title=template_name,
                ProductList=product_list
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Kits(WorksheetImporter):
    """ Import projects
    """
    def Import(self):

        pc = getToolByName(self.context, 'portal_catalog')

        rows = self.get_rows(3)
        for row in rows:
            # get the project
            project_list = pc(portal_type="Project", Title=row.get('Project'))
            if project_list:
                project = project_list[0].getObject()
            else:
                continue

            # get the kit template if it exists
            bsc = getToolByName(self.context, 'bika_setup_catalog')
            kit_template_list = bsc(portal_type="KitTemplate", title=row.get('KitTemplate'))
            kit_template = kit_template_list and kit_template_list[0].getObject() or None

            stock_items = []
            try:
                if kit_template:
                    stock_items = self.assign_stock_items(kit_template, row, bsc, pc)
            except ValueError as e:
                continue

            obj = _createObjectByType('Kit', project, tmpID())
            obj.edit(
                title=row.get('title'),
                description=row.get('description'),
                Project=project,
                KitTemplate=kit_template,
                FormsThere=row.get('FormsThere'),
                DateCreated=row.get('DateCreated', ''),
            )

            if kit_template:
                obj.setStockItems(stock_items)
                update_quantity_products(obj, bsc)

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def assign_stock_items(self, template, row, bsc, pc):

        si_storages = row.get('StockItemsStorage').split(',')

        if si_storages:
            si_storage_uids = []
            for storage in si_storages:
                storage_brains = pc(portal_type='UnmanagedStorage', Title=storage)
                storage_obj = storage_brains and storage_brains[0].getObject() or None
                if storage_obj:
                    si_storage_uids.append(storage_obj.UID())

        portal_workflow = getToolByName(self.context, 'portal_workflow')

        stock_items = template_stock_items(template, bsc, pc, portal_workflow, si_storage_uids)
        return stock_items


class Storage_Types(WorksheetImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.bika_setup.bika_storagetypes
        rows = self.get_rows(3)
        for row in rows:
            title = row.get('title')
            description = row.get('description', '')
            Temperature = row.get('Temperature')
            obj = _createObjectByType('StorageType', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                Temperature=Temperature
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

class DiseaseOntology(WorksheetImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.disease_ontologies
        rows = self.get_rows(3)
        for row in rows:
            title = row.get('title')
            description = row.get('description', '')
            version = row.get('Version')
            code = row.get('Code')
            free_text = row.get('FreeText')
            obj = _createObjectByType('DiseaseOntology', folder, tmpID())
            obj.edit(
                title=title,
                description=description,
                Version=version,
                Code=code,
                FreeText=free_text
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Donor(WorksheetImporter):
    """Add some dummy storage types
    """
    def Import(self):
        folder = self.context.donors
        rows = self.get_rows(3)

        pc = getToolByName(self.context, 'portal_catalog')

        for row in rows:
            sample_donor_id = row.get('SampleDonorID')
            selected_project = row.get('SelectedProject', '')
            info_link = row.get('InfoLink')
            sex = row.get('Sex')
            age = row.get('Age')
            age_unit = row.get('AgeUnit')
            obj = _createObjectByType('SampleDonor', folder, tmpID())

            # get the project
            project_list = pc(portal_type="Project", Title=selected_project)
            project = project_list and project_list[0].getObject() or None

            obj.edit(
                SampleDonorID=sample_donor_id,
                SelectedProject=project,
                InfoLink=info_link,
                Age=age,
                AgeUnit=age_unit
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class Projects(WorksheetImporter):
    """ Import projects
    """
    def Import(self):

        pc = getToolByName(self.context, 'portal_catalog')

        rows = self.get_rows(3)
        for row in rows:
            # get the client object
            client_list = pc(portal_type="Client", Title=row.get('Client'))

            folder = client_list and client_list[0].getObject() or None
            if not folder: continue

            s_types = row.get('SampleTypes')
            a_services = row.get('AnalysisServices')
            st_objects = get_project_multi_items(self.context, s_types, 'SampleType', 'bika_setup_catalog')
            as_objects = get_project_multi_items(self.context, a_services, 'AnalysisService', 'bika_setup_catalog')

            obj = _createObjectByType('Project', folder, tmpID())
            obj.edit(
                title=row.get('title'),
                description=row.get('description'),
                StudyType=row.get('StudyType', ''),
                AgeHigh=self.to_int(row.get('AgeHigh', 0)),
                AgeLow=self.to_int(row.get('AgeLow', 0)),
                NumParticipants=self.to_int(row.get('NumParticipants', 0)),
                SampleType=st_objects,
                Service=as_objects,
                DateCreated=row.get('DateCreated', ''),
            )

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)


class SampleImport(BaobabWorksheetImporter):
    """ Import biospecimens
    """

    def Import(self):

        self._pc = getToolByName(self.context, 'portal_catalog')
        self._bc = getToolByName(self.context, 'bika_catalog')
        self._wf = getToolByName(self.context, 'portal_workflow')
        self._errors = []

        rows = self.get_rows(3)
        for row in rows:
            try:
                self.create_biospecimen(row)
            except ExcelSheetError as e:
                self._errors.append(str(e))
                continue
            except Exception as e:
                self._errors.append(str(e))
                continue

    def get_storage_location(self, row_storage_location):
        storage_location = None
        if row_storage_location:
            st_loc_list = self._pc(portal_type='StoragePosition', Title=row_storage_location)
            storage_location = st_loc_list and st_loc_list[0].getObject() or None

        return storage_location

    def get_project(self, row_project):
        project_list = self._pc(portal_type="Project", Title=row_project)
        project = project_list and project_list[0].getObject() or None
        return project

    def get_sample_type(self, row_sample_type):
        sampletype_list = self._pc(portal_type="SampleType", Title=row_sample_type)
        sample_type = sampletype_list and sampletype_list[0].getObject() or None
        return sample_type

    def get_linked_sample(self, row_linked_sample):
        linked_sample_list = self._pc(portal_type="Sample", Title=row_linked_sample)
        linked_sample = linked_sample_list and linked_sample_list[0].getObject() or None
        return linked_sample

    def confirm_unique_title(self, title):
        if not title:
            return
        sample_list = self._pc(portal_type="Sample", Title=title)
        existing_sample = sample_list and sample_list[0].getObject() or None
        if existing_sample:
            raise ExcelSheetError('Sample with title or barcode %s already exists.' % title)

    def get_volume(self, row_volume):
        try:
            volume = str(row_volume)
            float_volume = float(volume)
            if not float_volume:
                raise ExcelSheetError('Invalid volume specified: %s' %row_volume)
            return str(float_volume)
        except Exception as e:
            # self._errors.append('Volume error has been found : %s' % str(e))
            raise ExcelSheetError('Volume error %s has been found : %s' % (row_volume, str(e)))


class ParentSample(SampleImport):
    """ Import biospecimens
    """

    def create_biospecimen(self, row):

        barcode = str(row.get('Barcode'))
        project = self.get_project(row.get('Project', ''))
        sample_type = self.get_sample_type(row.get('SampleType', ''))
        volume = self.get_volume(row.get('Volume', ''))
        title = row.get('title', barcode)
        self.confirm_unique_title(barcode)
        storage_location = self.get_storage_location(row.get('StorageLocation', ''))
        sampling_date = row.get('SamplingDate', '')

        if storage_location:
            storage_wf_state = self._wf.getInfoFor(storage_location, 'review_state')
            if storage_wf_state == 'occupied':
                raise ExcelSheetError('Import Error Sample %s: Storage %s already occupied.' % (title, storage_location.Title()))
        date_created = row.get('DateCreated', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M'))
        if not date_created:
            date_created = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')
        member = self.get_member()

        obj = _createObjectByType('Sample', project, tmpID())
        obj.edit(
            title=title,
            description=row.get('description'),
            Project=project,
            SampleType=sample_type,
            StorageLocation=storage_location,
            SubjectID=row.get('SubjectID'),
            Barcode=barcode,
            Volume=volume,
            Unit=row.get('Unit'),
            BabyNumber=row.get('BabyNo', ''),
            DateCreated=date_created,
            SamplingDate=sampling_date,
            # FrozenTime=row.get('FrozenTime'),
            ChangeUserName=member,
            ChangeDateTime=date_created,
        )

        obj.reindexObject()

        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

        from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
        ObjectInitializedEventHandler(obj, None)

class AliquotSample(SampleImport):
    """ Import biospecimens
    """

    def create_biospecimen(self, row):

        barcode = str(row.get('Barcode'))
        batch_id = str(row.get('BatchID', ''))

        brains = self._bc(portal_type='SampleBatch', title=batch_id)

        if brains:
            batch = brains[0].getObject()
        else:
            raise ExcelSheetError('Import Error Sample %s: Batch %s not found.' % (barcode, batch_id))

        parent = self.get_linked_sample(str(row.get('Parent', '')))
        if not parent:
            raise ExcelSheetError('Import Error Sample %s: Parent %s not found.' % (barcode, row.get('Parent', '')))

        project_obj = batch.getProject()

        sample_type = self.get_sample_type(row.get('SampleType', ''))
        volume = self.get_volume(row.get('Volume', ''))
        sampling_date = row.get('SamplingTime', '')

        title = row.get('Title', barcode)
        self.confirm_unique_title(barcode)

        storage_location = self.get_storage_location(row.get('StorageLocation', ''))
        if storage_location:
            storage_wf_state = analysis_state = self._wf.getInfoFor(storage_location, 'review_state')
            if storage_wf_state == 'occupied':
                raise ExcelSheetError('Import Error Sample %s: Storage %s already occupied.' % (barcode, storage_location.Title()))

        obj = _createObjectByType('Sample', project_obj, tmpID())
        field_b = obj.getField('Batch')
        field_b.set(obj, batch)

        date_created = row.get('DateCreated', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M'))
        if not date_created:
            date_created = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')

        unit = row.get('Unit', '')
        if not unit:
            raise ExcelSheetError(
                'Import Error Sample %s: Unit is a compulsory field.' % barcode)
        member = self.get_member()

        obj.edit(
            title=title,
            description=row.get('description'),
            Project=project_obj,
            SampleType=sample_type,
            StorageLocation=storage_location,
            SubjectID=row.get('SubjectID'),
            Barcode=barcode,
            Volume=volume,
            Unit=row.get('Unit'),
            # BabyNumber=row.get('BabyNo', ''),
            DateCreated=date_created,
            LinkedSample=parent,
            SamplingDate=sampling_date,
            FrozenTime=row.get('FrozenTime'),
            ChangeUserName=member,
            ChangeDateTime=date_created,
        )

        obj.reindexObject()

        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

        from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
        ObjectInitializedEventHandler(obj, None)


class SampleBatch(BaobabWorksheetImporter):
    """ Import biospecimens
    """

    def Import(self):
        folder = self.context.samplebatches
        rows = self.get_rows(3)
        self._errors = []

        self._pc = getToolByName(self.context, 'portal_catalog')

        for row in rows:
            selected_project = row.get('Project', '')
            #import pdb;pdb.set_trace()
            if selected_project:
                project_list = self._pc(portal_type="Project", Title=selected_project)
                project = project_list and project_list[0].getObject() or None
            else:
                continue
            subject_id = row.get('SubjectID')
            # sheet_parent_biospecimen = row.get('ParentBiospecimen', '')
            # parent_biospecimen = None
            # if sheet_parent_biospecimen:
            parent_biospecimen_text = str(row.get('ParentBiospecimen', ''))
            if parent_biospecimen_text:
                parent_biospecimen_list = self._pc(portal_type="Sample", Title=parent_biospecimen_text)
                parent_biospecimen = parent_biospecimen_list and parent_biospecimen_list[0].getObject() or None
                if not parent_biospecimen:
                    self._errors.append('Import batch error: Parent %s was not found' % parent_biospecimen_text)
                    continue
            else:
                self._errors.append('Import batch error: Parent sample cannot be blank.')

            # TODO: VERIFY IT LATER
            storage_locations = row.get('StorageLocations', '')
            boxes = self.getStorageLocations(storage_locations)

            batch_id = str(row.get('BatchID', ''))
            obj = _createObjectByType('SampleBatch', folder, tmpID())
            date_created = row.get('DateCreated', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M'))
            if not date_created:
                date_created = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')

            member = self.get_member()

            obj.edit(
                title=batch_id,
                Description=row.get('Description', ''),
                BatchId=batch_id,
                BatchType=row.get('BatchType', ''),
                Project=project,
                SubjectID=subject_id,
                StorageLocation=boxes,
                Quantity=row.get('Quantity', 0),
                ParentBiospecimen=parent_biospecimen,
                DateCreated=date_created,
                SerumColour=row.get('SerumColour', ''),
                CfgDateTime=row.get('CfgDateTime', ''),
                ChangeUserName=member,
                ChangeDateTime=date_created,
            )
            # import pdb;pdb.set_trace()
            obj.reindexObject()
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

    def get_sample_type(self, row_sample_type):
        sampletype_list = self._pc(portal_type="SampleType", Title=row_sample_type)
        sample_type = sampletype_list and sampletype_list[0].getObject() or None
        return sample_type

    def getStorageLocations(self, sheet_locations):
        sheet_locations = sheet_locations.split(',')
        storage_positions = []

        for sheet_location in sheet_locations:
            try:
                if sheet_location:
                    location_brains = self._pc(portal_type='StoragePosition', Title=sheet_location)
                    if location_brains:
                        for brain in location_brains:
                            storage_positions.append(brain.getObject())
            except:
                continue

        boxes = []
        for storage_position in storage_positions:
            if storage_position.aq_parent not in boxes:
                boxes.append(storage_position.aq_parent)

        return boxes








#
#
#     def create_aliquots(self, project, parent_sample, aliquot_sheet_name):
#
#         worksheet = self.workbook.get_sheet_by_name(aliquot_sheet_name)
#         if not worksheet:
#             return
#
#         pc = getToolByName(self.context, 'portal_catalog')
#         bc = getToolByName(self.context, 'bika_catalog')
#
#         for row in self.get_rows(3, worksheet=self.interim_worksheet):
#             create_sample(row, 'aliquot', project, parent_sample)
#
#
# def create_sample(row, aliquot_or_parent, project, sample_type, parent_sample=None):
#     # get the project
#     # project_list = pc(portal_type="Project", Title=row.get('Project'))
#     # project = project_list and project_list[0].getObject() or None
#     # if not project: raise ()
#
#     # sampletype_list = pc(portal_type="SampleType", Title=row.get('SampleType'))
#     # sample_type = sampletype_list and sampletype_list[0].getObject() or None
#     # if not sample_type: raise ()
#
#     # if aliquot_or_parent == 'parent':
#     #     linked_sample_list = pc(portal_type="Sample", Title=row.get('LinkedSample', ''))
#     #     linked_sample = linked_sample_list and linked_sample_list[0].getObject() or None
#
#     barcode = row.get('Barcode')
#     if not barcode:
#         raise ()
#
#     try:
#         volume = str(row.get('Volume'))
#         float_volume = float(volume)
#         if not float_volume:
#             raise ()
#     except:
#         raise ()
#
#     obj = _createObjectByType('Sample', project, tmpID())
#
#     st_loc_list = pc(portal_type='StoragePosition', Title=row.get('StorageLocation'))
#     storage_location = st_loc_list and st_loc_list[0].getObject() or None
#
#     obj.edit(
#         title=row.get('title'),
#         description=row.get('description'),
#         Project=project,
#         SampleType=sample_type,
#         StorageLocation=storage_location,
#         SubjectID=row.get('SubjectID'),
#         Barcode=barcode,
#         Volume=volume,
#         Unit=row.get('Unit'),
#         LinkedSample=parent_sample,
#         DateCreated=row.get('DateCreated'),
#         # AnatomicalSiteTerm=row.get('AnatomicalSiteTerm'),
#         # AnatomicalSiteDescription=row.get('AnatomicalSiteDescription'),
#     )
#
#     obj.unmarkCreationFlag()
#     renameAfterCreation(obj)
#
#     from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
#     ObjectInitializedEventHandler(obj, None)


class Biospecimens(WorksheetImporter):
    """ Import biospecimens
    """

    def Import(self):

        rows = self.get_rows(3)
        for row in rows:
            try:
                self.create_biospecimen(row)
            except:
                continue

    def create_biospecimen(self, row):
        pc = getToolByName(self.context, 'portal_catalog')
        bc = getToolByName(self.context, 'bika_catalog')

        # get the project
        project_list = pc(portal_type="Project", Title=row.get('Project'))
        project = project_list and project_list[0].getObject() or None
        if not project: raise

        sampletype_list = pc(portal_type="SampleType", Title=row.get('SampleType'))
        sample_type = sampletype_list and sampletype_list[0].getObject() or None
        if not sample_type: raise

        linked_sample_list = pc(portal_type="Sample", Title=row.get('LinkedSample', ''))
        linked_sample = linked_sample_list and linked_sample_list[0].getObject() or None

        sample_donor_list = bc(portal_type="SampleDonor", SampleDonorID=row.get('SampleDonor', ''))
        sample_donor = sample_donor_list and sample_donor_list[0].getObject() or None

        disease_ontology_list = bc(portal_type="DiseaseOntology", Title=row.get('DiseaseOntology', ''))
        disease_ontology = disease_ontology_list and disease_ontology_list[0].getObject() or None

        barcode = row.get('Barcode')
        if not barcode:
            raise

        try:
            volume = str(row.get('Volume'))
            float_volume = float(volume)
            if not float_volume:
                raise
        except:
            raise

        obj = _createObjectByType('Sample', project, tmpID())

        st_loc_list = pc(portal_type='StoragePosition', Title=row.get('StorageLocation'))
        storage_location = st_loc_list and st_loc_list[0].getObject() or None

        obj.edit(
            title=row.get('title'),
            description=row.get('description'),
            Project=project,
            DiseaseOntology=disease_ontology,
            Donor=sample_donor,
            SampleType=sample_type,
            StorageLocation=storage_location,
            SubjectID=row.get('SubjectID'),
            Barcode=barcode,
            Volume=volume,
            Unit=row.get('Unit'),
            LinkedSample=linked_sample,
            DateCreated=row.get('DateCreated', datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M')),
            AnatomicalSiteTerm=row.get('AnatomicalSiteTerm'),
            AnatomicalSiteDescription=row.get('AnatomicalSiteDescription'),

        )

        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

        from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
        ObjectInitializedEventHandler(obj, None)


class Storage(WorksheetImporter):
    """
    Import storage
    """
    def Import(self):

        rows = self.get_rows(3)
        for row in rows:

            # get the type of storage
            storage_type = row.get('type')
            if storage_type not in ['StorageUnit', 'ManagedStorage', 'UnmanagedStorage']:
                continue

            title = row.get('title')
            # get the parent
            hierarchy = row.get('hierarchy')
            parent = self.get_parent_storage(hierarchy)
            if not parent:
                print "parent not found for %s" % hierarchy
                continue





            storage_obj = _createObjectByType(storage_type, parent, row.get('id'))
            storage_obj.edit(
                title=title,
            )

            if storage_type == 'StorageUnit':
                bsc = getToolByName(self.context, 'bika_setup_catalog')
                facilities = bsc(portal_type="Department", title=row.get('Department'))
                facility = facilities and facilities[0].getObject() or None
                storage_types = bsc(portal_type="StorageType", title=row.get('StorageTypes'))
                storage_type = storage_types and storage_types[0].getObject() or None
                
                temperature = None
                if storage_type:
                    temperature = storage_type.getField('Temperature').get(storage_type)


                storage_obj.edit(
                    Department=facility,
                    UnitType=storage_type,
                    Temperature=temperature,
                )


            if storage_type == 'UnmanagedStorage':
                alsoProvides(storage_obj, IStockItemStorage)
                storage_obj.edit(
                    title=hierarchy,
                )

            if storage_type == 'ManagedStorage':
                storage_obj.edit(
                    XAxis=row.get('Columns'),
                    YAxis=row.get('Rows'),
                )
                alsoProvides(storage_obj, ISampleStorageLocation)

                nr_positions = row.get('NumberOfPoints')
                for p in range(1, nr_positions+1):
                    title = hierarchy + ".{id}".format(id=str(p).zfill(len(str(nr_positions))))
                    position = _createObjectByType('StoragePosition', storage_obj, str(p))
                    position.edit(
                        # title=hierarchy + ".{id}".format(id=p)
                        title=title
                    )
                    alsoProvides(position, ISampleStorageLocation)
                    position.reindexObject()

            storage_obj.unmarkCreationFlag()
            storage_obj.reindexObject()

    def get_parent_storage(self, hierarchy):

        pc = getToolByName(self.context, 'portal_catalog')
        hierarchy_pieces = hierarchy.split('.')

        if len(hierarchy_pieces) <= 1:
            return self.context.storage

        parent_id = hierarchy_pieces[len(hierarchy_pieces) - 2]
        parent_hierarchy = '.'.join(hierarchy_pieces[:-1])
        parent_list = pc(portal_type="StorageUnit", id=parent_id)

        if parent_list:
            for parent_item in parent_list:
                parent_object = parent_item.getObject()
                if parent_object.getHierarchy() == parent_hierarchy:
                    return parent_object


class StockItems(WorksheetImporter):
    """ Import stock items
    """
    def Import(self):
        folder = self.context.bika_setup.bika_stockitems
        rows = self.get_rows(3)
        bsc = getToolByName(self.context, 'bika_setup_catalog')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in rows:
            products = bsc(portal_type="Product", title=row.get('Product'))
            product = products and products[0].getObject() or None
            description = row.get('description', '')

            st_loc_list = pc(portal_type='UnmanagedStorage', Title=row.get('StorageLocation'))
            storage_location = st_loc_list and st_loc_list[0].getObject() or None

            obj = _createObjectByType('StockItem', folder, tmpID())
            obj.edit(
                Product=product,
                StorageLocation=storage_location,
                description=description,
                Quantity=self.to_int(row.get('Quantity', 0)),
                orderId=row.get('InvoiceNzr', ''),
                batchId=row.get('BatchNr', ''),
                receivedBy=row.get('ReceivedBy'),
                dateReceived=row.get('DateReceived', ''),
            )

            new_quantity = int(product.getQuantity()) + int(row.get('Quantity'))
            product.setQuantity(new_quantity)
            product.reindexObject()

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
