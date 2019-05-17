from Products.CMFCore.utils import getToolByName
from bika.lims.utils import to_utf8


class LabDataExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_lab_data = []

        lab = self.context.bika_setup.laboratory
        dict = {}
        dict['Title'] = lab.Title()
        dict['URL'] = lab.getLabURL()
        try:
            dict['Postal Address'] = self.getAddress(lab.getPostalAddress())
        except:
            dict['Postal Address'] = ''
        try:
            dict['Billing Address'] = self.getAddress(lab.getBillingAddress())
        except:
            dict['Billing Address'] = ''
        try:
            dict['Physical Address'] = self.getAddress(lab.getPhysicalAddress())
        except:
            dict['Physical Address'] = ''
        dict['Confidence'] = lab.getConfidence()
        dict['Accredited'] = lab.getLaboratoryAccredited()
        dict['Accreditation Body'] = to_utf8(lab.getAccreditationBody())
        # dict['Accreditation Logo'] = lab.getAccreditationLogo()

        list_of_lab_data.append(dict)
        return self.get_headings(), list_of_lab_data

    def getAddress(self, address):

        out_address = ', '.join(str(x) for x in address.values())
        return out_address

    def get_headings(self):
        headings = [
            'Title',
            'URL',
            'Postal Address',
            'Billing Address',
            'Physical Address',
            'Confidence',
            'Accredited',
            'Accreditation Body',
            # 'Accreditation Logo',
        ]

        return headings


# class LabDepartmentsExporter(object):
#     """ This class packages all the samples info into a list of dictionaries and then returns it.
#     """
#
#     def __init__(self, context):
#         self.context = context
#
#     def export(self):
#         list_of_lab_departments= []
#
#         pc = getToolByName(self.context, 'portal_catalog')
#         lab_department_brains = pc(portal_type="LabDepartment")
#         print('===brains========')
#
#         for brain in lab_department_brains:
#             lab_department = brain.getObject()
#             # print('-------------------')
#             # print(sample.__dict__)
#             dict = {}
#             dict['Title'] = lab_department.Title()
#             dict['Description'] = lab_department.Description()
#             # dict['RetentionPeriod'] = sample_type.getField('RetentionPeriod').get(sample_type)
#             dict['Hazardous'] = sample_type.getField('Hazardous').get(sample_type)
#             dict['Prefix'] = sample_type.getField('Prefix').get(sample_type)
#             dict['MinimumVolume'] = sample_type.getField('MinimumVolume').get(sample_type)
#
#             dict['UID'] = sample_type.UID()
#             try:
#                 dict['Parent_UID'] = sample_type.aq_parent.UID()
#             except:
#                 dict['Parent_UID'] = ''
#
#             list_of_sample_types.append(dict)
#
#         return self.get_headings(), list_of_sample_types
#
#     def get_headings(self):
#         headings = [
#             'Title',
#             'Description',
#             # 'RetentionPeriod',
#             'Hazardous',
#             'Prefix',
#             'MinimumVolume',
#             'UID',
#             'Parent_UID',
#         ]
#
#         return headings

class LabContactsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_lab_contacts = []

        pc = getToolByName(self.context, 'portal_catalog')
        lab_contact_brains = pc(portal_type="LabContact")
        print('===lab contact brains========')
        print(lab_contact_brains)

        for brain in lab_contact_brains:
            print('--------')

            lab_contact = brain.getObject()
            print(lab_contact.__dict__)
            dict = {}
            # dict['Title'] = 'This is a title'   #lab_contact.Title()
            # dict['Description'] = lab_contact.Description()
            dict['Salutation'] = lab_contact.getField('Salutation').get(lab_contact)
            dict['Firstname'] = lab_contact.getField('Firstname').get(lab_contact)
            dict['Surname'] = lab_contact.getField('Surname').get(lab_contact)
            dict['EmailAddress'] = lab_contact.getField('EmailAddress').get(lab_contact)
            dict['BusinessPhone'] = lab_contact.getField('BusinessPhone').get(lab_contact)
            dict['BusinessFax'] = lab_contact.getField('BusinessFax').get(lab_contact)
            dict['HomePhone'] = lab_contact.getField('HomePhone').get(lab_contact)
            dict['MobilePhone'] = lab_contact.getField('MobilePhone').get(lab_contact)
            dict['JobTitle'] = str(lab_contact.getField('JobTitle').get(lab_contact))
            # dict['Department'] = lab_contact.getField('Department').get(lab_contact)
            # dict['Username'] = lab_contact.getField('Username').get(lab_contact)
            # dict['Password'] = lab_contact.getField('Password').get(lab_contact)
            # dict['Groups'] = lab_contact.getField('Groups').get(lab_contact)
            # dict['Roles'] = lab_contact.getField('Roles').get(lab_contact)
            # dict['Signature'] = lab_contact.getField('Signature').get(lab_contact)
            dict['PhysicalAddress'] = self.getAddress(lab_contact.getField('PhysicalAddress').get(lab_contact))
            # dict['PhysicalCity'] = lab_contact.getField('PhysicalCity').get(lab_contact)
            # dict['PhysicalState'] = lab_contact.getField('PhysicalState').get(lab_contact)
            # dict['Physical_Zip'] = lab_contact.getField('Physical_Zip').get(lab_contact)
            # dict['Physical_Country'] = lab_contact.getField('Physical_Country').get(lab_contact)
            dict['PostalAddress'] = self.getAddress(lab_contact.getField('PostalAddress').get(lab_contact))

            # dict['Postal_City'] = lab_contact.getField('Postal_City').get(lab_contact)
            # dict['Postal_State'] = lab_contact.getField('Postal_State').get(lab_contact)
            # dict['Postal_Zip'] = lab_contact.getField('Postal_Zip').get(lab_contact)
            # dict['Postal_Country'] = lab_contact.getField('Postal_Country').get(lab_contact)
            # dict[''] = lab_contact.getField('').get(lab_contact)

            list_of_lab_contacts.append(dict)

        return self.get_headings(), list_of_lab_contacts

    def getAddress(self, address):

        out_address = ', '.join(str(x) for x in address.values())
        return out_address

    def get_headings(self):
        headings = [
            # 'Title',
            # 'Description',
            'Salutation',
            'Firstname',
            'Surname',
            'EmailAddress',
            'BusinessPhone',
            'BusinessFax',
            'HomePhone',
            'MobilePhone',
            'JobTitle',
            # 'Department',
            # 'Username',
            # 'Password',
            # 'Groups',
            # 'Roles',
            # 'Signature',
            'PhysicalAddress',
            # 'Physical_City',
            # 'Physical_State',
            # 'Physical_Zip',
            # 'Physical_Country',
            'PostalAddress',
            # 'Postal_City',
            # 'Postal_State',
            # 'Postal_Zip',
            # 'Postal_Country',
        ]

        return headings


class AnalysisCategoriesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_analysis_categories = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        analysis_category_brains = bsc(portal_type="AnalysisCategory")
        print('===brains========')

        for brain in analysis_category_brains:
            analysis_category = brain.getObject()
            # print('-------------------')
            # print(analysis_category.__dict__)
            dict = {}
            dict['Title'] = analysis_category.Title()
            dict['Description'] = analysis_category.Description()
            dict['Comments'] = analysis_category.getField('Comments').get(analysis_category)

            department = analysis_category.getField('Department').get(analysis_category)
            try:
                dict['Department'] = department.Title()
            except:
                dict['Department'] = ''

            dict['UID'] = analysis_category.UID()
            try:
                dict['Parent_UID'] = analysis_category.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_analysis_categories.append(dict)

        return self.get_headings(), list_of_analysis_categories

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'Comments',
            'Department',
            'UID',
            'Parent_UID',
        ]

        return headings

class AnalysisServicesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_analysis_services = []

        bsc = getToolByName(self.context, 'bika_setup_catalog')
        analysis_service_brains = bsc(portal_type="AnalysisService")
        print('===brains========')

        for brain in analysis_service_brains:
            analysis_service = brain.getObject()
            # print('-------------------')
            # print(analysis_category.__dict__)
            dict = {}
            dict['Title'] = analysis_service.Title()
            dict['Description'] = analysis_service.Description()
            dict['ShortTitle'] = analysis_service.getField('ShortTitle').get(analysis_service)
            dict['Keyword'] = analysis_service.getField('Keyword').get(analysis_service)
            dict['PointOfCapture'] = analysis_service.getField('PointOfCapture').get(analysis_service)
            dict['Category'] = analysis_service.getField('Category').get(analysis_service)
            department = analysis_service.getField('Department').get(analysis_service)
            try:
                dict['Department'] = department.Title()
            except:
                dict['Department'] = ''
            dict['ReportDryMatter'] = analysis_service.getField('ReportDryMatter').get(analysis_service)
            dict['AttachmentOption'] = analysis_service.getField('AttachmentOption').get(analysis_service)
            dict['Unit'] = analysis_service.getField('Unit').get(analysis_service)
            dict['Precision'] = analysis_service.getField('Precision').get(analysis_service)
            dict['ExponentialFormatPrecision'] = analysis_service.getField('ExponentialFormatPrecision').get(analysis_service)
            dict['LowerDetectionLimit'] = analysis_service.getField('LowerDetectionLimit').get(analysis_service)
            dict['UpperDetectionLimit'] = analysis_service.getField('UpperDetectionLimit').get(analysis_service)
            dict['DetectionLimitSelector'] = analysis_service.getField('DetectionLimitSelector').get(analysis_service)
            dict['MaxTimeAllowed'] = analysis_service.getField('MaxTimeAllowed').get(analysis_service)
            dict['Price'] = analysis_service.getField('Price').get(analysis_service)
            dict['BulkPrice'] = analysis_service.getField('BulkPrice').get(analysis_service)
            # dict['VatAmount'] = analysis_service.getField('VatAmount').get(analysis_service)
            dict['TotalPrice'] = analysis_service.getField('TotalPrice').get(analysis_service)
            dict['Price'] = analysis_service.getField('Price').get(analysis_service)
            dict['BulkPrice'] = analysis_service.getField('BulkPrice').get(analysis_service)
            # dict['Vat'] = analysis_service.getField('Vat').get(analysis_service)
            dict['TotalPrice'] = analysis_service.getField('TotalPrice').get(analysis_service)
            dict['ManualEntryOfResults'] = analysis_service.getField('ManualEntryOfResults').get(analysis_service)
            #
            dict['Instruments'] = analysis_service.getField('Instruments').get(analysis_service)
            #
            dict['Methods'] = analysis_service.getField('Methods').get(analysis_service)

            dict['ScientificName'] = analysis_service.getField('ScientificName').get(analysis_service)
            dict['AllowManualDetectionLimit'] = analysis_service.getField('AllowManualDetectionLimit').get(analysis_service)
            dict['ReportDryMatter'] = analysis_service.getField('ReportDryMatter').get(analysis_service)
            dict['AttachmentOption'] = analysis_service.getField('AttachmentOption').get(analysis_service)
            dict['InstrumentEntryOfResults'] = analysis_service.getField('InstrumentEntryOfResults').get(analysis_service)
            #
            # dict['_Method'] = analysis_service.getField('_Method').get(analysis_service)
            dict['CalculationTitle'] = analysis_service.getField('CalculationTitle').get(analysis_service)
            dict['DuplicateVariation'] = analysis_service.getField('DuplicateVariation').get(analysis_service)
            dict['Accredited'] = analysis_service.getField('Accredited').get(analysis_service)
            dict['Separate'] = analysis_service.getField('Separate').get(analysis_service)
            # dict['Container'] = analysis_service.getField('Container').get(analysis_service)
            # dict['Preservation'] = analysis_service.getField('Preservation').get(analysis_service)

            # department = analysis_category.getField('Department').get(analysis_category)
            # try:
            #     dict['Department'] = department.Title()
            # except:
            #     dict['Department'] = ''

            dict['UID'] = analysis_service.UID()
            try:
                dict['Parent_UID'] = analysis_service.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_analysis_services.append(dict)

        return self.get_headings(), list_of_analysis_services

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'ShortTitle',
            'Keyword',
            'PointOfCapture',
            'Category',
            'Department',
            'ReportDryMatter',
            'AttachmentOption',
            'Unit',
            'Precision',
            'ExponentialFormatPrecision',
            'LowerDetectionLimit',
            'UpperDetectionLimit',
            'DetectionLimitSelector',
            'MaxTimeAllowed',
            'Price',
            'BulkPrice',
            # 'VatAmount',
            'TotalPrice',
            'Price',
            'BulkPrice',
            # 'Vat',
            'TotalPrice',
            'ManualEntryOfResults',
            #
            'Instruments',
            #
            'Methods',
            'ScientificName',
            'AllowManualDetectionLimit',
            'ReportDryMatter',
            'AttachmentOption',
            'InstrumentEntryOfResults',
            #
            #'_Method',
            'CalculationTitle',
            'DuplicateVariation',
            'Accredited',
            'Separate',
            #'Container',
            #'Preservation',
        ]

        return headings


class SampleTypesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_sample_types = []

        pc = getToolByName(self.context, 'portal_catalog')
        sample_type_brains = pc(portal_type="SampleType")
        # print('===brains========')
        if sample_type_brains:
            list_of_sample_types.append(['Title', 'Description', 'Hazardous', 'Prefix', 'MinimumVolume', 'HasBabyNumber'])

        for brain in sample_type_brains:
            sample_type = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            # dict = {}
            # dict['Title'] = sample_type.Title()
            # dict['Description'] = sample_type.Description()
            # # dict['RetentionPeriod'] = sample_type.getField('RetentionPeriod').get(sample_type)
            # dict['Hazardous'] = sample_type.getField('Hazardous').get(sample_type)
            # dict['Prefix'] = sample_type.getField('Prefix').get(sample_type)
            # dict['MinimumVolume'] = sample_type.getField('MinimumVolume').get(sample_type)
            #
            # dict['UID'] = sample_type.UID()
            # try:
            #     dict['Parent_UID'] = sample_type.aq_parent.UID()
            # except:
            #     dict['Parent_UID'] = ''

            row = []
            row.append(str(sample_type.Title()))
            row.append(str(sample_type.Description()).rstrip())
            row.append(sample_type.getField('Hazardous').get(sample_type))
            row.append(sample_type.getField('Prefix').get(sample_type))
            row.append(sample_type.getField('MinimumVolume').get(sample_type))
            row.append(sample_type.getField('HasBabyNumber').get(sample_type))
            # row.append(sample_type.UID())
            # row.append(sample_type.aq_parent.UID() if sample_type.aq_parent.UID() else '')

            # list_of_sample_types.append(dict)
            list_of_sample_types.append(row)

        # return self.get_headings(), list_of_sample_types
        return list_of_sample_types

    # def get_headings(self):
    #     headings = [
    #         'Title',
    #         'Description',
    #         # 'RetentionPeriod',
    #         'Hazardous',
    #         'Prefix',
    #         'MinimumVolume',
    #         'UID',
    #         'Parent_UID',
    #     ]
    #
    #     return headings


class ClientsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_clients = []

        pc = getToolByName(self.context, 'portal_catalog')
        client_brains = pc(portal_type="Client")
        print('===brains========')

        for brain in client_brains:
            client = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = client.Title()
            dict['Description'] = client.Description()
            dict['EmailAddress'] = client.getEmailAddress()
            dict['Phone'] = client.getPhone()
            dict['Fax'] = client.getFax()
            dict['ClientID'] = client.getClientID()
            dict['BulkDiscount'] = client.getBulkDiscount()
            dict['MemberDiscountApplies'] = client.getMemberDiscountApplies()

            dict['UID'] = client.UID()
            try:
                dict['Parent_UID'] = client.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_clients.append(dict)

        return self.get_headings(), list_of_clients

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'EmailAddress',
            'Phone',
            'Fax',
            'ClientID',
            'BulkDiscount',
            'MemberDiscountApplies',
            'UID',
            'Parent_UID',
        ]

        return headings


class ProjectsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_projects = []

        pc = getToolByName(self.context, 'portal_catalog')
        project_brains = pc(portal_type="Project")
        print('===brains========')

        for brain in project_brains:
            project = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = project.Title()
            dict['Description'] = project.Description()
            dict['StudyType'] = project.getField('StudyType').get(project)
            dict['EthicsFormLink'] = project.getField('EthicsFormLink').get(project)
            dict['AgeHigh'] = project.getField('AgeHigh').get(project)
            dict['AgeLow'] = project.getField('AgeLow').get(project)
            dict['NumParticipants'] = project.getField('NumParticipants').get(project)
            # dict[''] = project.getField('').get(project)
            # dict[''] = project.getField('').get(project)
            # dict['DateCreated'] = project.getField('DateCreated').get(project)
            # dict[''] = project.getField('').get(project)

            # TODO:  Add service and sample typesz

            dict['UID'] = project.UID()
            try:
                dict['Parent_UID'] = project.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_projects.append(dict)

        return self.get_headings(), list_of_projects

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'StudyType',
            'EthicsFormLink',
            'AgeHigh',
            'AgeLow',
            'NumParticipants',
            # '',
            # '',
            # 'DateCreated',
            'UID',
            'Parent_UID',
        ]

        return headings


class SampleBatchesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        sample_batches = []
        bc = getToolByName(self.context, 'bika_catalog')
        brains = bc(portal_type="SampleBatch")
        if brains:
            sample_batches.append(['Title', 'Description', 'Project', 'Subject_ID', 'Parent_Biospecimen_Kit_ID',
                                   'Batch_ID', 'Batch_Type', 'Storage_Locations', 'Date_Created', 'Serum_Colour',
                                   'Cfg_Time', 'Quantity'])
        for brain in brains:
            sample_batch = brain.getObject()
            if sample_batch:
                row = []
                row.append(str(sample_batch.Title()))
                row.append(str(sample_batch.Description()).rstrip())

                # project
                project = sample_batch.getProject()
                project_title = ''
                if project:
                    project_title = project.Title()
                row.append(project_title)

                row.append(sample_batch.getSubjectID())
                parent_biospecimen_title = ''
                parent_biospecimen = sample_batch.getParentBiospecimen()
                if parent_biospecimen:
                    parent_biospecimen_title = parent_biospecimen.Title()
                row.append(parent_biospecimen_title)
                row.append(str(sample_batch.getBatchId()))
                row.append(sample_batch.getBatchType())

                if sample_batch.getStorageLocation():
                    locations = []
                    for location in sample_batch.getStorageLocation():
                        locations.append(str(location.getHierarchy()))
                    row.append(','.join(locations))
                else:
                    row.append('')
                if sample_batch.getDateCreated():
                    row.append(sample_batch.getDateCreated().strftime("%Y-%m-%d %H:%M"))
                else:
                    row.append('')
                row.append(sample_batch.getSerumColour())
                if sample_batch.getCfgDateTime():
                    row.append(sample_batch.getCfgDateTime().strftime("%Y-%m-%d %H:%M"))
                else:
                    row.append('')
                row.append(sample_batch.getQuantity())

                sample_batches.append(row)
        return sample_batches

class SamplesExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        samples = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="Sample")
        if brains:
            samples.append(['Title', 'Project_Visit_Type', 'Sample_Type','Storage_Location', 'Sampling_Time',
                            'Subject_ID', 'Barcode_Kit_ID', 'Volume', 'Unit', 'Baby_No', 'Sample_State',
                            'Date_Created', 'Last Modified By', 'Last Modify Date'])
        for brain in brains:
            sample = brain.getObject()
            if not sample.getField('LinkedSample').get(sample):
                row = []
                row.append(sample.Title())
                # project = sample.getField('Project').get(sample)
                project = sample.aq_parent
                row.append(project.Title())
                row.append(sample.getSampleType().Title())
                storage = sample.getField('StorageLocation').get(sample)
                if storage:
                    row.append(storage.getHierarchy())
                else:
                    row.append('')
                row.append(sample.getSamplingDate().strftime("%Y-%m-%d %H:%M") if sample.getSamplingDate() else '')
                row.append(sample.getField('SubjectID').get(sample))
                row.append(sample.getField('Barcode').get(sample))
                row.append(sample.getField('Volume').get(sample))
                row.append(sample.getField('Unit').get(sample))
                # row.append(sample.getField('BabyNumber').get(sample))

                baby_number = sample.getField('BabyNumber').get(sample) if sample.getField('BabyNumber') else ''
                if baby_number == '0' or baby_number == 0:
                    baby_number = ''
                # print "Parent - babynumber type: " + str(type(baby_number))
                # print "Parent - babynumber value: " + str(baby_number)
                row.append(baby_number)

                row.append(sample.getSampleState())
                row.append(sample.getField('DateCreated').get(sample).strftime("%Y-%m-%d %H:%M") if sample.getField('DateCreated').get(sample) else '')

                last_modified_user = sample.getField('ChangeUserName').get(sample)
                last_modified_date = ''
                if sample.getField('ChangeDateTime').get(sample):
                    last_modified_date = sample.getField('ChangeDateTime').get(sample).strftime("%Y-%m-%d %H:%M")
                row.append(last_modified_user)
                row.append(last_modified_date)

                # row.append(sample.getField('SampleID').get(sample))

                samples.append(row)
        return samples

class SamplesAliquotExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        aliquots = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="Sample")
        if brains:
            aliquots.append(['Title', 'Sample_Type', 'Subject_ID', 'Barcode', 'Volume',
                             'Unit', 'Storage', 'Frozen_Time', 'Sample_State', 'Sampling_Time',
                             'Parent_Biospecimen_Kit_ID', 'Batch_ID', 'Baby_No', 'Date_Created', 'Sample_ID',
                            'Last Modified By', 'Last Modify Date'])
        for brain in brains:
            sample = brain.getObject()
            parent_sample = sample.getField('LinkedSample').get(sample)
            if parent_sample:

                batch = sample.getField('Batch').get(sample) and sample.getField('Batch').get(sample).Title() or ''
                row = []
                row.append(sample.Title())
                row.append(sample.getSampleType().Title())
                row.append(sample.getField('SubjectID').get(sample))
                row.append(sample.getField('Barcode').get(sample))
                row.append(sample.getField('Volume').get(sample))
                row.append(sample.getField('Unit').get(sample))

                storage = sample.getField('StorageLocation').get(sample)
                if storage:
                    row.append(storage.getHierarchy())
                else:
                    row.append('')                
                # row.append(sample.getField('SamplingDate').get(sample))
                row.append(sample.getField('FrozenTime').get(sample).strftime("%Y-%m-%d %H:%M") if sample.getField('FrozenTime').get(sample) else '')
                row.append(sample.getSampleState())
                row.append(sample.getField('SamplingDate').get(sample).strftime("%Y-%m-%d %H:%M") if sample.getField('SamplingDate').get(sample) else '')
                row.append(parent_sample.getField('Barcode').get(parent_sample))
                row.append(batch)

                baby_number = parent_sample.getField('BabyNumber').get(parent_sample) if parent_sample.getField('BabyNumber') else ''
                # if baby_number == 0:
                #     baby_number = sample.getField('BabyNumber').get(sample) if sample.getField('BabyNumber') else 0
                if baby_number == '0' or baby_number == 0:
                    baby_number = ' '
                # print "Aliquot - babynumber type: " + str(type(baby_number))
                # print "Aliquot - babynumber value: " + str(baby_number)
                row.append(baby_number)

                row.append(sample.getField('DateCreated').get(sample).strftime("%Y-%m-%d %H:%M") if sample.getField('DateCreated').get(sample) else '')
                row.append(sample.getField('SampleID').get(sample))

                last_modified_user = sample.getField('ChangeUserName').get(sample)
                last_modified_date = ''
                if sample.getField('ChangeDateTime').get(sample):
                    last_modified_date = sample.getField('ChangeDateTime').get(sample).strftime("%Y-%m-%d %H:%M")
                row.append(last_modified_user)
                row.append(last_modified_date)

                aliquots.append(row)
        return aliquots

class BoxMovementExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        box_movements = []
        pc = getToolByName(self.context, 'portal_catalog')
        brains = pc(portal_type="BoxMovement")
        if brains:
            box_movements.append(['Title', 'Description', 'Old_Location', 'Lab_Contact', 'New_Location', 'Date_Moved'])

        for brain in brains:
            box_move = brain.getObject()
            row = []
            row.append(box_move.Title())
            row.append(box_move.getField('description').get(box_move) if box_move.getField('description') else '')
            old_storage = box_move.getField('StorageLocation').get(box_move)
            if old_storage:
                row.append(str(old_storage.getHierarchy()))
            else:
                row.append('')
            row.append(box_move.getLabContact().Title())
            new_location = box_move.getField('NewLocation').get(box_move)
            if new_location:
                row.append(str(new_location.getHierarchy()))
            else:
                row.append('')
            if box_move.getDateCreated():
                row.append(box_move.getDateCreated().strftime("%Y-%m-%d %H:%M"))
            else:
                row.append('')
            box_movements.append(row)
        return box_movements


class SampleShipmentExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
        Returns all the samples except Aliquots (Samples with Parent Samples/LinkedSample)
    """
    def __init__(self, context):
        self.context = context

    def export(self):
        sample_shipments = []
        pc = getToolByName(self.context, 'bika_catalog')
        brains = pc(portal_type="SampleShipment")

        if brains:
            sample_shipments.append(['Title', 'Description', 'Date_Delivered', 'Date_Dispatched',
                                     'Shipping_Date', 'Samples', 'Volume','Weight', 'Shipping_Cost', 'Shipping_Conditions',
                                     'Tracking_URL', 'Courier_Instructions', 'Courier', 'Billing_Address',
                                     'Delivery_Address', 'Client', 'Receiver_Email_Address', 'Sender_Email_Address'])

        for brain in brains:
            shipment = brain.getObject()
            if shipment:
                row = []
                row.append(shipment.Title())
                row.append(str(shipment.Description()).rstrip())
                row.append(shipment.getField('DateDelivered').get(shipment).strftime("%Y-%m-%d %H:%M") if shipment.getField('DateDelivered').get(shipment) else '')
                row.append(shipment.getField('DateDispatched').get(shipment).strftime("%Y-%m-%d %H:%M") if shipment.getField('DateDispatched').get(shipment) else '')
                row.append(shipment.getField('ShippingDate').get(shipment).strftime("%Y-%m-%d %H:%M") if shipment.getField('ShippingDate').get(shipment) else '')
                row.append(str([sample.id for sample in shipment.getField('SamplesList').get(shipment)]) if shipment.getField('SamplesList') else '')
                row.append(str(shipment.getField('Volume').get(shipment)) if shipment.getField('Volume') else '')
                row.append(str(shipment.getField('Weight').get(shipment)) if shipment.getField('Weight') else '')
                row.append(str(shipment.getField('ShippingCost').get(shipment)) if shipment.getField('ShippingCost') else '')
                row.append(str(shipment.getField('ShipmentConditions').get(shipment)) if shipment.getField('ShipmentConditions') else '')
                row.append(str(shipment.getField('TrackingURL').get(shipment)) if shipment.getField('TrackingURL') else '')
                row.append(str(shipment.getField('CourierInstructions').get(shipment)) if shipment.getField('CourierInstructions') else '')
                row.append(str(shipment.getField('Courier').get(shipment)))
                row.append(str(shipment.getField('BillingAddress').get(shipment)) if shipment.getField('BillingAddress') else '')
                row.append(str(shipment.getField('DeliveryAddress').get(shipment)))
                row.append(str(shipment.getField('Client').get(shipment).ClientID))
                row.append(str(shipment.getField('ToEmailAddress').get(shipment)) if shipment.getField('ToEmailAddress') else '')
                row.append(str(shipment.getField('FromEmailAddress').get(shipment)) if shipment.getField('FromEmailAddress') else '')

                sample_shipments.append(row)
        return sample_shipments



class AnalysisRequestsExporter(object):
    """ This class packages all the samples info into a list of dictionaries and then returns it.
    """

    def __init__(self, context):
        self.context = context

    def export(self):
        list_of_analysis_requests = []

        pc = getToolByName(self.context, 'portal_catalog')
        analysis_request_brains = pc(portal_type="AnalysisRequest")
        print('===brains========')

        for brain in analysis_request_brains:
            analysis_request = brain.getObject()
            # print('-------------------')
            # print(sample.__dict__)
            dict = {}
            dict['Title'] = analysis_request.Title()
            dict['Description'] = analysis_request.Description()
            dict['RequestID'] = analysis_request.getField('RequestID').get(analysis_request)
            project = analysis_request.getField('Project').get(analysis_request)
            try:
                dict['Project'] = project.Title()
            except:
                dict['Project'] = ''

            contact = analysis_request.getField('Contact').get(analysis_request)
            try:
                dict['Contact'] = contact.Title()
            except:
                dict['Contact'] = ''

            cc_contact = analysis_request.getField('CCContact').get(analysis_request)
            try:
                dict['CCContact'] = cc_contact.Title()
            except:
                dict['CCContact'] = ''

            dict['CCEmails'] = analysis_request.getField('CCEmails').get(analysis_request)

            client = analysis_request.getField('Client').get(analysis_request)
            try:
                dict['Client'] = client.Title()
            except:
                dict['Client'] = ''

            sample = analysis_request.getField('Sample').get(analysis_request)
            try:
                dict['Sample'] = sample.Title()
            except:
                dict['Sample'] = ''
            dict['Volume'] = analysis_request.getField('Volume').get(analysis_request)

            specification = analysis_request.getField('Specification').get(analysis_request)
            try:
                dict['Specification'] = specification.Title()
            except:
                dict['Specification'] = ''

            dict['ResultsRange'] = analysis_request.getField('ResultsRange').get(analysis_request)

            publication_specification = analysis_request.getField('PublicationSpecification').get(analysis_request)
            try:
                dict['PublicationSpecification'] = publication_specification.Title()
            except:
                dict['PublicationSpecification'] = ''

            dict['ClientOrderNumber'] = analysis_request.getField('ClientOrderNumber').get(analysis_request)
            dict['ReportDryMatter'] = analysis_request.getField('ReportDryMatter').get(analysis_request)
            dict['InvoiceExclude'] = analysis_request.getField('InvoiceExclude').get(analysis_request)
            dict['DateReceived'] = analysis_request.getField('DateReceived').get(analysis_request)
            dict['DatePublished'] = analysis_request.getField('DatePublished').get(analysis_request)
            dict['Remarks'] = analysis_request.getField('Remarks').get(analysis_request)
            # dict[''] = analysis_request.getField('').get(analysis_request)

            dict['UID'] = sample.UID()
            try:
                dict['Parent_UID'] = sample.aq_parent.UID()
            except:
                dict['Parent_UID'] = ''

            list_of_analysis_requests.append(dict)

        return self.get_headings(), list_of_analysis_requests

    def get_headings(self):
        headings = [
            'Title',
            'Description',
            'RequestID',
            'Contact',
            'CCContact',
            'CCEmails',
            'Client',
            'Sample',
            'Volume',
            'Specification',
            'ResultRange',
            'PublicationSpecification',
            'ClientOrderNumber',
            'ReportDryMatter',
            'InvoiceExclude',
            'DateReceived',
            'DatePublished',
            'Remarks',
            'UID',
            'Parent_UID',
        ]

        return headings
