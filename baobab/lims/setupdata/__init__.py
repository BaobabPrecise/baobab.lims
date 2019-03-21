from bika.lims.exportimport.dataimport import SetupDataSetList as SDL
from bika.lims.exportimport.setupdata import WorksheetImporter
from Products.CMFPlone.utils import _createObjectByType
from bika.lims.interfaces import ISetupDataSetList
from zope.interface import implements
from zope.interface import alsoProvides
from baobab.lims.idserver import renameAfterCreation
from baobab.lims.interfaces import ISampleStorageLocation, IStockItemStorage
from baobab.lims.browser.project import *


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


class SetupDataSetList(SDL):

    implements(ISetupDataSetList)

    def __call__(self):
        return SDL.__call__(self, projectname="baobab.lims")


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
            obj = _createObjectByType('StorageType', folder, tmpID())
            obj.edit(
                title=title,
                description=description
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


class SampleImport(WorksheetImporter):
    """ Import biospecimens
    """

    def Import(self):

        self._pc = getToolByName(self.context, 'portal_catalog')
        self._bc = getToolByName(self.context, 'bika_catalog')

        rows = self.get_rows(3)
        for row in rows:
            try:
                self.create_biospecimen(row)
            except:
                continue

    def get_storage_location(self, row_storage_location):
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


    def get_volume(self, row_volume):
        try:
            volume = str(row_volume)
            float_volume = float(volume)
            if not float_volume:
                raise ()
            return str(float_volume)
        except Exception as e:
            print('Error has been found : %s' % str(e))
            raise ()


class ParentSample(SampleImport):
    """ Import biospecimens
    """

    def create_biospecimen(self, row):
        barcode = row.get('Barcode')
        if not barcode:
            raise ()

        project = self.get_project(row.get('Project', ''))
        if not project:
            raise()

        sample_type = self.get_sample_type(row.get('SampleType', ''))
        if not sample_type:
            raise()

        volume = self.get_volume(row.get('Volume', ''))

        obj = _createObjectByType('Sample', project, tmpID())

        self.complete_biospecimen(obj, sample_type, barcode, volume, row)

    def complete_biospecimen(self, obj, sample_type, barcode, volume, row):
        storage_location = self.get_storage_location(row.get('StorageLocation', ''))

        obj.edit(
            title=row.get('title'),
            description=row.get('description'),
            Project=project,
            SampleType=sample_type,
            StorageLocation=storage_location,
            SubjectID=row.get('SubjectID'),
            Barcode=barcode,
            Volume=volume,
            Unit=row.get('Unit'),
            BabyNumber=row.get('BabyNo', ''),
            # LinkedSample=linked_sample,
            DateCreated=row.get('DateCreated'),
            # AnatomicalSiteTerm=row.get('AnatomicalSiteTerm'),
            # AnatomicalSiteDescription=row.get('AnatomicalSiteDescription'),
        )

        obj.reindexObject()

        obj.unmarkCreationFlag()
        renameAfterCreation(obj)

        from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
        ObjectInitializedEventHandler(obj, None)




class SampleBatch(WorksheetImporter):
    """ Import biospecimens
    """

    def Import(self):
        folder = self.context.samplebatches
        rows = self.get_rows(3)

        self._pc = getToolByName(self.context, 'portal_catalog')

        for row in rows:
            try:
                selected_project = row.get('Project', '')
                try:
                    project_list = self._pc(portal_type="Project", Title=selected_project)
                    project = project_list and project_list[0].getObject() or None
                except:
                    raise()
                subject_id = row.get('SubjectID')
                if not subject_id:
                    raise()
                parent_biospecimen_list = self._pc(portal_type="Sample", Title=row.get('ParentBiospecimen', ''))
                parent_biospecimen = parent_biospecimen_list and parent_biospecimen_list[0].getObject() or None

                boxes, storage_locations = self.getStorageLocations(row.get('StorageLocations', ''))

                # print("-------------")
                # print(boxes)
                # print(storage_locations)

                obj = _createObjectByType('SampleBatch', folder, tmpID())
                obj.edit(
                    Title='samplebatchtmptitle',
                    Description=row.get('Description', ''),
                    BatchType=row.get('BatchType', ''),
                    Project=project,
                    SubjectID=subject_id,
                    StorageLocation=boxes,
                    ParentBiospecimen=parent_biospecimen,
                    DateCreated=row.get('DateCreated', ''),
                    SerumColor=row.get('SerumColor', ''),
                    CfgDateTime=row.get('CfgDateTime', ''),
                )
                obj.reindexObject()

                obj.unmarkCreationFlag()
                renameAfterCreation(obj)

                self.createAliquots(row.get('AliquotSheetName'), project, obj.UID())

            except:
                continue

    def createAliquots(self, sheet_name, project, batch_uid):

        worksheet = self.workbook.get_sheet_by_name(sheet_name)

        rows = self.get_rows(3, worksheet=worksheet)
        # aliquot_gen = AliquotSample()
        for row in rows:
            self.create_biospecimen(project, batch_uid, row)

    def create_biospecimen(self, project, batch_uid, row):
        barcode = row.get('Barcode')
        if not barcode:
            raise ()
        sample_type = self.get_sample_type(row.get('SampleType', ''))
        if not sample_type:
            raise()

        volume = self.get_volume(row.get('Volume', ''))

        obj = _createObjectByType('Sample', project, tmpID())
        field_b = obj.getField('Batch')
        field_b.set(obj, batch_uid)

        self.complete_biospecimen(obj, sample_type, barcode, volume, row)

    def complete_biospecimen(self, obj, sample_type, barcode, volume, row):
        try:
            st_loc_list = self._pc(portal_type='StoragePosition', Title=row.get('StorageLocation', ''))
            storage_location = st_loc_list and st_loc_list[0].getObject() or None

            obj.edit(
                title=row.get('title'),
                description=row.get('description'),
                Project=project,
                SampleType=sample_type,
                StorageLocation=storage_location,
                SubjectID=row.get('SubjectID'),
                Barcode=barcode,
                Volume=volume,
                Unit=row.get('Unit'),
                BabyNumber=row.get('BabyNo', ''),
                # LinkedSample=linked_sample,
                DateCreated=row.get('DateCreated'),
                # AnatomicalSiteTerm=row.get('AnatomicalSiteTerm'),
                # AnatomicalSiteDescription=row.get('AnatomicalSiteDescription'),
            )

            obj.reindexObject()

            obj.unmarkCreationFlag()
            renameAfterCreation(obj)

            from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
            ObjectInitializedEventHandler(obj, None)
        except Exception as e:
            print('Exception is %s' % str(e))

    def get_volume(self, row_volume):
        try:
            volume = str(row_volume)
            float_volume = float(volume)
            if not float_volume:
                raise ()
            return str(float_volume)
        except Exception as e:
            raise ()

    def get_sample_type(self, row_sample_type):
        sampletype_list = self._pc(portal_type="SampleType", Title=row_sample_type)
        sample_type = sampletype_list and sampletype_list[0].getObject() or None
        return sample_type


    def getStorageLocations(self, sheet_locations):

        sheet_locations = sheet_locations.split(',')
        print(sheet_locations)
        storage_positions = []

        for sheet_location in sheet_locations:
            try:
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

        return boxes, storage_positions


# class AliquotSample(SampleImport):
#     """ Import biospecimens
#     """
#
#     # def Import(self, aliquot_sheet_name, parent_sample):
#     #
#     #     worksheet = self.workbook.get_sheet_by_name(aliquot_sheet_name)
#     #     if not worksheet:
#     #         return
#     #
#     #     for row in self.get_rows(3, worksheet=self.interim_worksheet):
#     #         create_sample(row, project, parent_sample)
#     #
#
#     def __init__(self):
#         self._pc = getToolByName(self.context, 'portal_catalog')
#         self._bc = getToolByName(self.context, 'bika_catalog')
#
#     def create_biospecimen(self, batch_uid, row):
#         print("===create aliquot===1")
#         barcode = row.get('Barcode')
#         if not barcode:
#             raise ()
#         print("===create aliquot===2")
#         project = self.get_project(row.get('Project', ''))
#         if not project:
#             raise()
#         print("===create aliquot===3")
#         sample_type = self.get_sample_type(row.get('SampleType', ''))
#         if not sample_type:
#             raise()
#         print("===create aliquot===4")
#         volume = self.get_volume(row.get('Volume', ''))
#         print("===create aliquot===5")
#         obj = _createObjectByType('Sample', project, tmpID())
#         print("===create aliquot===6")
#         field_b = obj.getField('Batch')
#         field_b.set(obj, batch_uid)
#         print("===create aliquot===7")
#         self.complete_biospecimen(obj, sample_type, barcode, volume, row)
#         print("===create aliquot===8")
#     def complete_biospecimen(self, obj, sample_type, barcode, volume, row):
#         storage_location = self.get_storage_location(row.get('StorageLocation', ''))
#
#         obj.edit(
#             title=row.get('title'),
#             description=row.get('description'),
#             Project=project,
#             SampleType=sample_type,
#             StorageLocation=storage_location,
#             SubjectID=row.get('SubjectID'),
#             Barcode=barcode,
#             Volume=volume,
#             Unit=row.get('Unit'),
#             BabyNumber=row.get('BabyNo', ''),
#             # LinkedSample=linked_sample,
#             DateCreated=row.get('DateCreated'),
#             # AnatomicalSiteTerm=row.get('AnatomicalSiteTerm'),
#             # AnatomicalSiteDescription=row.get('AnatomicalSiteDescription'),
#         )
#
#         obj.reindexObject()
#
#         obj.unmarkCreationFlag()
#         renameAfterCreation(obj)
#
#         from baobab.lims.subscribers.sample import ObjectInitializedEventHandler
#         ObjectInitializedEventHandler(obj, None)





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
            DateCreated=row.get('DateCreated'),
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

